"""
API Routes for Hospital Search Endpoints
"""

from fastapi import APIRouter

from ..models.schemas import NearbyHospitalsRequest, NearbyHospitalsResponse
from ..services.hospital_service import find_nearby_hospitals

router = APIRouter(prefix="/api/v1", tags=["hospitals"])


@router.post("/nearby-hospitals", response_model=NearbyHospitalsResponse)
async def nearby_hospitals(request: NearbyHospitalsRequest) -> NearbyHospitalsResponse:
    """
    Find nearby hospitals with smart filtering and condition-based scoring.
    
    This endpoint uses Google Places API to find hospitals near the user's location,
    filters out diagnostic centers and labs, and scores hospitals based on
    their relevance to the patient's condition.
    
    - **lat**: Latitude coordinate
    - **lng**: Longitude coordinate  
    - **symptoms**: Optional symptom description for condition-based matching
    
    Returns a list of up to 5 hospitals sorted by relevance and distance.
    """
    return await find_nearby_hospitals(request)
