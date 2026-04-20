"""
Pydantic Models for API Requests and Responses
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TriageRequest(BaseModel):
    """Request model for symptom triage analysis."""
    symptoms: str = Field(..., min_length=10, max_length=1000, description="Detailed symptom description")
    request_id: Optional[str] = Field(None, description="Optional tracking ID for the request")

    @field_validator('symptoms')
    @classmethod
    def validate_symptoms(cls, v: str) -> str:
        """Validate symptom input."""
        # Strip whitespace
        v = v.strip()
        # Check length
        if len(v) < 10:
            raise ValueError("Symptoms must be at least 10 characters long")
        if len(v) > 1000:
            raise ValueError("Symptoms must be less than 1000 characters")
        return v


class TriageResponse(BaseModel):
    """Response model for triage analysis results."""
    priority: int = Field(..., ge=1, le=4, description="Priority level (1=Critical, 2=High, 3=Medium, 4=Low)")
    priority_label: str = Field(..., description="Human-readable priority label")
    reason: str = Field(..., description="Clinical reasoning for priority assessment")
    action: str = Field(..., description="Recommended action for patient")
    queue: str = Field(..., description="Queue recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score (0.0-1.0)")
    escalation_triggers: list[str] = Field(default_factory=list, description="Conditions requiring escalation")
    disclaimer: str = Field(..., description="Medical disclaimer")
    blocked: bool = Field(default=False, description="Whether request was blocked for safety")
    blocked_reason: Optional[str] = Field(None, description="Reason if request was blocked")
    condition_category: Optional[str] = Field(None, description="Categorized condition type")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: int) -> int:
        """Ensure priority is in valid range."""
        if not 1 <= v <= 4:
            raise ValueError("Priority must be between 1 and 4")
        return v

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class NearbyHospitalsRequest(BaseModel):
    """Request model for finding nearby hospitals."""
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="User latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="User longitude")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Legacy: User latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Legacy: User longitude")
    location: Optional[str] = Field(None, min_length=2, max_length=100, description="City or area name")
    condition: Optional[str] = Field(None, description="Medical condition category")
    symptoms: Optional[str] = Field(None, description="Patient symptoms")

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str]) -> Optional[str]:
        """Validate location string."""
        if v:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Location must be at least 2 characters")
        return v


class HospitalInfo(BaseModel):
    """Information about a single hospital."""
    name: str = Field(..., min_length=1, description="Hospital name")
    address: str = Field(..., description="Hospital address")
    distance: float = Field(..., ge=0, description="Distance in km")
    distance_text: str = Field(..., description="Formatted distance text")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    place_id: Optional[str] = Field(None, description="Google Maps place ID")
    score: int = Field(default=0, ge=0, le=100, description="Match score (0-100)")
    match_tag: str = Field(default="Nearby Option", description="Why this hospital is recommended")
    phone: Optional[str] = Field(None, description="Contact phone number")
    is_open: Optional[bool] = Field(None, description="Whether hospital is currently open")


class NearbyHospitalsResponse(BaseModel):
    """Response model for nearby hospitals search."""
    success: bool = Field(..., description="Whether search was successful")
    hospitals: list[HospitalInfo] = Field(default_factory=list, description="List of nearby hospitals")
    error: Optional[str] = Field(None, description="Error message if search failed")
    condition_category: Optional[str] = Field(None, description="Categorized condition type")
    safety_message: Optional[str] = Field(None, description="Additional safety information")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    model: str = Field(..., description="AI model in use")
    version: str = Field(..., description="API version")

