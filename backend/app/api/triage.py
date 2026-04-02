"""
API Routes for Triage Endpoints
"""

from fastapi import APIRouter

from ..models.schemas import TriageRequest, TriageResponse
from ..services.triage_service import analyze_symptoms

router = APIRouter(prefix="/api/v1", tags=["triage"])


@router.post("/analyze", response_model=TriageResponse)
async def analyze(request: TriageRequest) -> TriageResponse:
    """
    Analyze patient symptoms and return triage priority.
    
    This endpoint takes a description of patient symptoms and uses AI
    to classify the urgency level, providing recommendations for care.
    
    - **symptoms**: Detailed description of patient symptoms
    - **request_id**: Optional tracking ID for the request
    
    Returns triage priority (1-4), recommendations, and escalation triggers.
    """
    return await analyze_symptoms(request)
