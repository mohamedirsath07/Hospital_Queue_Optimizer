"""API routes for triage endpoints."""

from datetime import datetime
import structlog
from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models import (
    ErrorResponse,
    HealthResponse,
    TriageRequest,
    TriageResponse,
)
from app.services import llm_service, safety_service

logger = structlog.get_logger()
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint",
)
async def health_check() -> HealthResponse:
    """Check if the service is running."""
    return HealthResponse(status="healthy", version="1.0.0")


@router.post(
    "/analyze",
    response_model=TriageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "LLM service unavailable"},
    },
    tags=["Triage"],
    summary="Analyze patient symptoms and return triage priority",
    description="""
    Analyzes patient-reported symptoms using AI and returns a structured triage assessment.

    **Safety Features:**
    - Pre-LLM keyword detection for critical symptoms (auto-escalation)
    - Post-LLM output validation (no diagnosis/treatment advice)
    - Low-confidence escalation (fail-safe behavior)

    **Important:** This is a triage aid, NOT a diagnostic tool.
    All results should be reviewed by qualified healthcare staff.
    """,
)
async def analyze_symptoms(request: TriageRequest) -> TriageResponse:
    """
    Analyze patient symptoms and determine triage priority.

    Steps:
    1. Pre-filter: Check for critical keywords requiring immediate escalation
    2. LLM Analysis: Get AI-based urgency classification
    3. Post-filter: Validate and sanitize LLM output
    4. Priority Calculation: Combine all factors for final priority
    """
    settings = get_settings()

    logger.info(
        "Triage request received",
        request_id=request.request_id,
        symptoms_length=len(request.symptoms),
    )

    try:
        # Step 1: Pre-filter safety check
        pre_priority, pre_flags, pre_reasoning = safety_service.pre_filter(request.symptoms)

        if pre_priority == 1:
            # Critical keyword detected - bypass LLM for speed
            logger.warning(
                "Critical keyword detected - immediate escalation",
                request_id=request.request_id,
                flags=[f.code for f in pre_flags],
            )
            return TriageResponse(
                priority=1,
                priority_label="CRITICAL",
                reason=pre_reasoning or "Critical symptoms detected requiring immediate attention",
                action="Immediate staff response required",
                queue="critical-care",
                confidence=1.0,
                safety_flags=pre_flags,
                escalation_triggers=[
                    "Loss of consciousness",
                    "Worsening symptoms",
                    "New severe symptoms",
                ],
                request_id=request.request_id,
            )

        # Step 2: LLM Analysis
        try:
            llm_response = await llm_service.analyze_symptoms(request)
        except Exception as e:
            logger.error("LLM service error", error=str(e), request_id=request.request_id)
            # Fail-safe: escalate to urgent on LLM failure
            return TriageResponse(
                priority=2,
                priority_label="EMERGENT",
                reason="System unable to complete analysis - escalating for safety",
                action="Immediate staff assessment required",
                queue="emergency",
                confidence=0.0,
                safety_flags=pre_flags
                + [
                    {
                        "code": "LLM_FAILURE",
                        "severity": "high",
                        "message": "AI analysis unavailable - manual triage required",
                    }
                ],
                escalation_triggers=[],
                request_id=request.request_id,
            )

        # Step 3: Post-filter validation
        llm_response, post_flags = safety_service.post_filter(llm_response)
        all_flags = pre_flags + post_flags

        # Step 4: Calculate final priority
        llm_priority = llm_response.get("priority", 3)
        confidence = llm_response.get("confidence", 0.5)

        final_priority = safety_service.calculate_final_priority(
            llm_priority=llm_priority,
            pre_filter_priority=pre_priority,
            confidence=confidence,
            confidence_threshold=settings.safety_confidence_threshold,
        )

        # Build response
        response = TriageResponse(
            priority=final_priority,
            priority_label=llm_service.get_priority_label(final_priority),
            reason=llm_response.get("reason", "Evaluation required"),
            action=llm_response.get("action", "Staff assessment required"),
            queue=llm_response.get("queue", llm_service.get_queue_for_priority(final_priority)),
            confidence=confidence,
            safety_flags=all_flags,
            escalation_triggers=llm_response.get("escalation_triggers", []),
            request_id=request.request_id,
            timestamp=datetime.utcnow(),
        )

        logger.info(
            "Triage completed",
            request_id=request.request_id,
            priority=final_priority,
            confidence=confidence,
            flags_count=len(all_flags),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in triage", request_id=request.request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="Internal server error",
                detail=str(e) if settings.debug else None,
                request_id=request.request_id,
            ).model_dump(),
        )
