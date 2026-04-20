"""
Triage Service
Handles symptom analysis and AI-powered triage classification.
"""

import json
import logging
import httpx
from typing import Optional

from ..core.config import get_settings
from ..core.constants import CONDITION_KEYWORDS, PRIORITY_LABELS, DISCLAIMER
from ..core.safety import check_input_safety, get_safe_response
from ..models.schemas import TriageRequest, TriageResponse

logger = logging.getLogger(__name__)


# LLM System Prompt
SYSTEM_PROMPT = """You are a medical triage classification assistant. Your ONLY role is to classify the URGENCY of patient symptoms.

RULES (NEVER VIOLATE):
1. NEVER diagnose or name medical conditions
2. NEVER recommend medications or treatments
3. NEVER dismiss patient concerns
4. When uncertain, choose MORE urgent

PRIORITY LEVELS:
- 1 (CRITICAL): Life-threatening, immediate attention
- 2 (URGENT): Serious, needs prompt attention
- 3 (SEMI-URGENT): Needs attention within 1 hour
- 4 (NON-URGENT): Minor, can wait

Respond with ONLY valid JSON:
{
  "priority": <1-4>,
  "reason": "<brief symptom summary, NO diagnosis>",
  "action": "<what staff should do>",
  "queue": "<critical-care|urgent-care|standard-care|routine>",
  "confidence": <0.0-1.0>,
  "escalation_triggers": ["<warning sign to watch>"]
}"""


def classify_condition(symptoms: str) -> str:
    """
    Classify patient condition based on symptoms using keyword matching.

    Args:
        symptoms: Patient symptom description

    Returns:
        Condition category (CARDIAC, TRAUMA, NEURO, GENERAL, or OTHER)
    """
    symptoms_lower = symptoms.lower()

    for condition, keywords in CONDITION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in symptoms_lower:
                return condition

    return "OTHER"


def _extract_json_from_response(content: str) -> dict:
    """
    Safely extract JSON from LLM response that may contain markdown code blocks.

    Args:
        content: Raw response content from LLM

    Returns:
        Parsed JSON dictionary

    Raises:
        ValueError: If JSON cannot be extracted or parsed
        JSONDecodeError: If JSON is malformed
    """
    if not content or not isinstance(content, str):
        raise ValueError(f"Invalid response content: {type(content)}")

    # Try to extract JSON from code blocks
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        else:
            content = content.strip()

        if not content:
            raise ValueError("Empty content after extraction")

        # Parse JSON
        parsed = json.loads(content)

        if not isinstance(parsed, dict):
            raise ValueError(f"Expected JSON object, got {type(parsed)}")

        return parsed

    except (IndexError, KeyError) as e:
        raise ValueError(f"Failed to extract JSON from response: {e}")


def _validate_priority_response(parsed: dict) -> dict:
    """
    Validate and normalize LLM response, ensuring all fields are valid.

    Args:
        parsed: Parsed JSON from LLM

    Returns:
        Validated and normalized response dictionary
    """
    # Validate and constrain priority
    priority = parsed.get("priority", 3)
    try:
        priority = int(priority)
        if not 1 <= priority <= 4:
            logger.warning(f"Invalid priority {priority}, clamping to valid range")
            priority = max(1, min(4, priority))
    except (ValueError, TypeError):
        logger.warning(f"Invalid priority type: {priority}, using default 3")
        priority = 3

    # Validate and constrain confidence
    confidence = parsed.get("confidence", 0.7)
    try:
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            logger.warning(f"Invalid confidence {confidence}, clamping to valid range")
            confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        logger.warning(f"Invalid confidence type: {confidence}, using default 0.7")
        confidence = 0.7

    # Extract and validate other fields
    reason = str(parsed.get("reason", "Evaluation required"))[:500]
    action = str(parsed.get("action", "Staff assessment required"))[:500]
    queue = str(parsed.get("queue", "standard-care"))
    escalation_triggers = parsed.get("escalation_triggers", [])

    if not isinstance(escalation_triggers, list):
        escalation_triggers = [str(escalation_triggers)]

    escalation_triggers = [str(t)[:200] for t in escalation_triggers[:5]]

    return {
        "priority": priority,
        "reason": reason,
        "action": action,
        "queue": queue,
        "confidence": confidence,
        "escalation_triggers": escalation_triggers
    }


async def analyze_symptoms(request: TriageRequest) -> TriageResponse:
    """
    Analyze patient symptoms and return triage priority.

    Args:
        request: TriageRequest with symptoms

    Returns:
        TriageResponse with priority and recommendations
    """
    settings = get_settings()

    # Classify condition for hospital matching
    condition_category = classify_condition(request.symptoms)

    logger.info(f"Starting triage analysis - Condition: {condition_category}, RequestID: {request.request_id}")

    # Safety check
    is_safe, block_reason = check_input_safety(request.symptoms)
    if not is_safe:
        logger.warning(f"Blocked unsafe input: {block_reason}")
        safe_response = get_safe_response(block_reason)
        return TriageResponse(
            priority=2,
            priority_label="URGENT",
            reason=safe_response["message"],
            action=safe_response["action"],
            queue="urgent-care",
            confidence=1.0,
            escalation_triggers=[],
            disclaimer=DISCLAIMER,
            blocked=True,
            blocked_reason=block_reason,
            condition_category=condition_category
        )

    # Call Groq API
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Patient symptoms: {request.symptoms}\n\nClassify urgency. JSON only."}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise ValueError("Empty response from LLM")

            # Parse and validate JSON response
            try:
                parsed = _extract_json_from_response(content)
                validated = _validate_priority_response(parsed)
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"JSON parsing error: {e}. Returning fallback response.")
                return _create_fallback_response(condition_category, "Unable to complete analysis - defaulting to urgent evaluation")

            return TriageResponse(
                priority=validated["priority"],
                priority_label=PRIORITY_LABELS.get(validated["priority"], "SEMI-URGENT"),
                reason=validated["reason"],
                action=validated["action"],
                queue=validated["queue"],
                confidence=validated["confidence"],
                escalation_triggers=validated["escalation_triggers"],
                disclaimer=DISCLAIMER,
                condition_category=condition_category
            )

    except httpx.HTTPStatusError as e:
        logger.error(f"API Error: {e.response.status_code} - {e.response.text}")
        return _create_fallback_response(condition_category, "System temporarily unavailable - defaulting to urgent for safety")
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout after 30s: {e}")
        return _create_fallback_response(condition_category, "Analysis timed out - defaulting to urgent for your safety")
    except Exception as e:
        logger.exception(f"Unexpected error during triage analysis: {e}")
        return _create_fallback_response(condition_category, "Server error occurred - defaulting to urgent for safety")


def _create_fallback_response(condition_category: str, reason: str) -> TriageResponse:
    """Create a safe fallback response when analysis fails."""
    return TriageResponse(
        priority=2,
        priority_label="URGENT",
        reason=reason,
        action="Please seek immediate medical evaluation as a precaution",
        queue="urgent-care",
        confidence=0.0,
        escalation_triggers=["If symptoms worsen, call emergency services"],
        disclaimer=DISCLAIMER,
        condition_category=condition_category
    )

