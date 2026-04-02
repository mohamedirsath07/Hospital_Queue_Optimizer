"""
Pydantic Models for API Requests and Responses
"""

from typing import Optional
from pydantic import BaseModel


class TriageRequest(BaseModel):
    """Request model for symptom triage analysis."""
    symptoms: str
    request_id: Optional[str] = None


class TriageResponse(BaseModel):
    """Response model for triage analysis results."""
    priority: int
    priority_label: str
    reason: str
    action: str
    queue: str
    confidence: float
    escalation_triggers: list[str]
    disclaimer: str
    blocked: bool = False
    blocked_reason: Optional[str] = None
    condition_category: Optional[str] = None


class NearbyHospitalsRequest(BaseModel):
    """Request model for finding nearby hospitals."""
    lat: float
    lng: float
    symptoms: Optional[str] = None


class HospitalInfo(BaseModel):
    """Information about a single hospital."""
    name: str
    address: str
    distance: float
    distance_text: str
    lat: float
    lng: float
    place_id: Optional[str] = None
    score: int = 0
    match_tag: str = "Nearby Option"
    phone: Optional[str] = None
    is_open: Optional[bool] = None


class NearbyHospitalsResponse(BaseModel):
    """Response model for nearby hospitals search."""
    success: bool
    hospitals: list[HospitalInfo]
    error: Optional[str] = None
    condition_category: Optional[str] = None
    safety_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model: str
    version: str
