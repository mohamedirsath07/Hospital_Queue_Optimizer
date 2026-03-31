"""LLM service for interacting with Groq API."""

import json
from typing import Any
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.models import TriageRequest, PriorityLevel

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are a medical triage classification assistant. Your ONLY role is to classify the URGENCY of patient symptoms. You are NOT a doctor and must NEVER diagnose conditions or recommend treatments.

CORE RULES (NEVER VIOLATE):
1. NEVER provide a diagnosis or suggest what condition the patient has
2. NEVER recommend any medication, dosage, or treatment
3. NEVER tell patients they don't need to see a doctor
4. NEVER minimize or dismiss patient concerns
5. When uncertain, ALWAYS choose the MORE urgent classification

URGENCY LEVELS:
- 1 (CRITICAL): Immediate life threat
- 2 (EMERGENT): Potential life threat, severe distress
- 3 (URGENT): Significant symptoms requiring prompt evaluation
- 4 (LESS_URGENT): Minor acute issues, stable
- 5 (NON_URGENT): Routine, can wait

You must respond with ONLY a valid JSON object in this exact format:
{
  "priority": <number 1-5>,
  "reason": "<brief objective summary of symptoms, NO diagnosis>",
  "action": "<staff action required>",
  "queue": "<queue-name>",
  "confidence": <number 0.0-1.0>,
  "escalation_triggers": ["<symptom to watch for>", ...]
}

Queue names: "critical-care", "emergency", "urgent-care", "standard-care", "routine"

Remember: You classify URGENCY, not CAUSE. Never suggest what might be wrong."""


def _build_user_prompt(request: TriageRequest) -> str:
    """Build the user prompt from triage request."""
    parts = [f"Patient reports: {request.symptoms}"]

    if request.vital_signs:
        vitals = []
        vs = request.vital_signs
        if vs.heart_rate is not None:
            vitals.append(f"HR: {vs.heart_rate}")
        if vs.blood_pressure_systolic is not None and vs.blood_pressure_diastolic is not None:
            vitals.append(f"BP: {vs.blood_pressure_systolic}/{vs.blood_pressure_diastolic}")
        if vs.temperature_celsius is not None:
            vitals.append(f"Temp: {vs.temperature_celsius}C")
        if vs.oxygen_saturation is not None:
            vitals.append(f"SpO2: {vs.oxygen_saturation}%")
        if vs.respiratory_rate is not None:
            vitals.append(f"RR: {vs.respiratory_rate}")
        if vitals:
            parts.append(f"Vital signs: {', '.join(vitals)}")

    if request.patient_context:
        ctx = request.patient_context
        context_parts = []
        if ctx.age is not None:
            context_parts.append(f"Age: {ctx.age}")
        if ctx.is_pregnant:
            context_parts.append("Pregnant")
        if ctx.is_immunocompromised:
            context_parts.append("Immunocompromised")
        if ctx.known_conditions:
            context_parts.append(f"History: {', '.join(ctx.known_conditions)}")
        if context_parts:
            parts.append(f"Patient context: {', '.join(context_parts)}")

    parts.append("\nClassify the urgency level. Respond with JSON only.")
    return "\n".join(parts)


class LLMService:
    """Service for LLM interactions via Groq API."""

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(
            base_url=self.settings.groq_base_url,
            headers={
                "Authorization": f"Bearer {self.settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.settings.llm_timeout,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def analyze_symptoms(self, request: TriageRequest) -> dict[str, Any]:
        """
        Send symptoms to LLM for triage classification.

        Returns parsed JSON response from LLM.
        """
        user_prompt = _build_user_prompt(request)

        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.1,  # Low temperature for consistent classification
            "max_tokens": 500,
            "response_format": {"type": "json_object"},
        }

        logger.info(
            "Calling LLM",
            model=self.settings.groq_model,
            request_id=request.request_id,
        )

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            logger.info(
                "LLM response received",
                priority=parsed.get("priority"),
                confidence=parsed.get("confidence"),
                request_id=request.request_id,
            )

            return parsed

        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response", error=str(e))
            # Return safe defaults
            return {
                "priority": PriorityLevel.URGENT,
                "reason": "Unable to parse AI response - defaulting to urgent",
                "action": "Staff assessment required",
                "queue": "urgent-care",
                "confidence": 0.0,
                "escalation_triggers": [],
            }
        except httpx.HTTPStatusError as e:
            logger.error(
                "LLM API error",
                status_code=e.response.status_code,
                detail=e.response.text[:200],
            )
            raise

    def get_priority_label(self, priority: int) -> str:
        """Get human-readable label for priority level."""
        labels = {
            1: "CRITICAL",
            2: "EMERGENT",
            3: "URGENT",
            4: "LESS_URGENT",
            5: "NON_URGENT",
        }
        return labels.get(priority, "UNKNOWN")

    def get_queue_for_priority(self, priority: int) -> str:
        """Get queue name for priority level."""
        queues = {
            1: "critical-care",
            2: "emergency",
            3: "urgent-care",
            4: "standard-care",
            5: "routine",
        }
        return queues.get(priority, "urgent-care")


# Singleton instance
llm_service = LLMService()
