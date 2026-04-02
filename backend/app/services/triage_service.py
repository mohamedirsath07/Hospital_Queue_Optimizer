"""
Triage Service
Handles symptom analysis and AI-powered triage classification.
"""

import json
import httpx
from typing import Optional

from ..core.config import get_settings
from ..core.constants import CONDITION_KEYWORDS, PRIORITY_LABELS, DISCLAIMER
from ..core.safety import check_input_safety, get_safe_response
from ..models.schemas import TriageRequest, TriageResponse


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
    
    # Safety check
    is_safe, block_reason = check_input_safety(request.symptoms)
    if not is_safe:
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
            
            content = data["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed = json.loads(content.strip())
            priority = parsed.get("priority", 3)
            
            return TriageResponse(
                priority=priority,
                priority_label=PRIORITY_LABELS.get(priority, "SEMI-URGENT"),
                reason=parsed.get("reason", "Evaluation required"),
                action=parsed.get("action", "Staff assessment required"),
                queue=parsed.get("queue", "standard-care"),
                confidence=parsed.get("confidence", 0.7),
                escalation_triggers=parsed.get("escalation_triggers", []),
                disclaimer=DISCLAIMER,
                condition_category=condition_category
            )
            
    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}")
        return _create_fallback_response(condition_category, "System temporarily unavailable - defaulting to urgent for safety")
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        return _create_fallback_response(condition_category, "Unable to complete analysis - defaulting to urgent evaluation")
    except httpx.TimeoutException:
        print("Request timeout")
        return _create_fallback_response(condition_category, "Analysis timed out - defaulting to urgent for your safety")
    except Exception as e:
        print(f"Error: {e}")
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
