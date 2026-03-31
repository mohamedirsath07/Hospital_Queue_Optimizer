"""Pydantic models for request/response schemas."""

from datetime import datetime
from enum import IntEnum
from typing import Optional
from pydantic import BaseModel, Field


class PriorityLevel(IntEnum):
    """Triage priority levels (1 = most urgent)."""

    CRITICAL = 1
    EMERGENT = 2
    URGENT = 3
    LESS_URGENT = 4
    NON_URGENT = 5


class VitalSigns(BaseModel):
    """Optional vital signs data."""

    heart_rate: Optional[int] = Field(None, ge=0, le=300)
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200)
    temperature_celsius: Optional[float] = Field(None, ge=30.0, le=45.0)
    oxygen_saturation: Optional[int] = Field(None, ge=0, le=100)
    respiratory_rate: Optional[int] = Field(None, ge=0, le=60)


class PatientContext(BaseModel):
    """Optional patient context for risk adjustment."""

    age: Optional[int] = Field(None, ge=0, le=150)
    is_pregnant: bool = False
    is_immunocompromised: bool = False
    known_conditions: list[str] = Field(default_factory=list)


class TriageRequest(BaseModel):
    """Request body for /analyze endpoint."""

    symptoms: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Patient-reported symptoms as free text",
    )
    vital_signs: Optional[VitalSigns] = None
    patient_context: Optional[PatientContext] = None
    request_id: Optional[str] = Field(None, description="Client-provided request ID for tracing")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "symptoms": "I have a severe headache and feel nauseous",
                    "vital_signs": {"temperature_celsius": 38.5},
                    "patient_context": {"age": 45},
                }
            ]
        }
    }


class SafetyFlag(BaseModel):
    """Safety flag triggered during analysis."""

    code: str
    severity: str
    message: str


class TriageResponse(BaseModel):
    """Response body for /analyze endpoint."""

    priority: int = Field(..., ge=1, le=5, description="Urgency level 1-5")
    priority_label: str = Field(..., description="Human-readable priority label")
    reason: str = Field(..., description="Brief explanation for classification")
    action: str = Field(..., description="Recommended next step for staff")
    queue: str = Field(..., description="Queue assignment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    safety_flags: list[SafetyFlag] = Field(default_factory=list)
    escalation_triggers: list[str] = Field(
        default_factory=list,
        description="Symptoms patient should watch for",
    )
    disclaimer: str = Field(
        default="This is a triage assessment only, not a medical diagnosis. "
        "A qualified healthcare professional must evaluate the patient.",
    )
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "priority": 3,
                    "priority_label": "URGENT",
                    "reason": "Headache with nausea requires evaluation",
                    "action": "Schedule for assessment within 60 minutes",
                    "queue": "urgent-care",
                    "confidence": 0.85,
                    "safety_flags": [],
                    "escalation_triggers": [
                        "Sudden severe worsening",
                        "Neck stiffness",
                        "Vision changes",
                    ],
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
