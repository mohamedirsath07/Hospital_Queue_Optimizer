"""
AI Hospital Triage System - Single File Backend
With Smart Hospital Filtering & Condition-Based Matching
Run: python main.py
"""

import os
import re
import json
import math
from pathlib import Path
from typing import Optional
from datetime import datetime

# Load .env file if exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().strip().split("\n"):
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# =============================================================================
# VERSION AND CONFIGURATION
# =============================================================================

APP_VERSION = "1.1.0"
APP_NAME = "AI Hospital Triage System"
START_TIME = datetime.now()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not set. Set it via environment variable.")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
HOSPITAL_SEARCH_RADIUS = 5000  # 5km radius

# =============================================================================
# HOSPITAL FILTERING CONFIGURATION
# =============================================================================

# Keywords that indicate NON-hospital places (to be filtered out)
EXCLUDED_KEYWORDS = [
    "diagnostic", "diagnostics", "lab", "laboratory", "laboratories",
    "scan", "scanning", "imaging", "pathology", "path lab",
    "x-ray", "xray", "mri", "ct scan", "ultrasound",
    "pharmacy", "medical store", "chemist",
    "dental", "dentist", "eye clinic", "optical",
    "physiotherapy", "physio", "rehab center",
    "nursing home", "old age", "hospice",
    "blood bank", "test", "testing"
]

# Keywords that indicate VALID hospitals
VALID_HOSPITAL_KEYWORDS = [
    "hospital", "medical center", "medical centre",
    "emergency", "trauma center", "trauma centre",
    "multi-speciality", "multispeciality", "multi-specialty", "multispecialty",
    "general hospital", "govt hospital", "government hospital"
]

# Condition categories and their keyword triggers
CONDITION_KEYWORDS = {
    "CARDIAC": [
        "chest pain", "heart", "cardiac", "breathing difficulty", "breathless",
        "shortness of breath", "palpitation", "heart attack", "angina"
    ],
    "TRAUMA": [
        "injury", "injured", "accident", "bleeding", "fracture", "broken",
        "wound", "cut", "burn", "fall", "trauma", "hit", "crash"
    ],
    "NEURO": [
        "unconscious", "seizure", "convulsion", "stroke", "paralysis",
        "numbness", "headache severe", "fainting", "blackout", "fits"
    ],
    "GENERAL": [
        "fever", "infection", "cold", "cough", "flu", "vomiting",
        "diarrhea", "stomach", "pain", "weakness", "fatigue"
    ]
}

# Hospital preferences by condition
CONDITION_HOSPITAL_PREFERENCES = {
    "CARDIAC": ["cardiac", "heart", "multi-speciality", "multispeciality", "general"],
    "TRAUMA": ["trauma", "emergency", "accident", "multi-speciality", "general"],
    "NEURO": ["neuro", "brain", "multi-speciality", "multispeciality", "general"],
    "GENERAL": ["general", "multi-speciality", "multispeciality", "hospital"],
    "OTHER": ["general", "multi-speciality", "hospital"]
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def classify_condition(symptoms: str) -> str:
    """Classify patient condition based on symptoms using keyword matching."""
    symptoms_lower = symptoms.lower()
    
    # Check each condition category
    for condition, keywords in CONDITION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in symptoms_lower:
                return condition
    
    return "OTHER"


def is_valid_hospital(name: str) -> bool:
    """Check if a place is a valid hospital (not a diagnostic center/lab)."""
    name_lower = name.lower()
    
    # First, check if it contains excluded keywords
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            # Exception: if it also contains "hospital", it might be valid
            if "hospital" not in name_lower:
                return False
    
    # Check if it contains at least one valid hospital keyword
    for valid in VALID_HOSPITAL_KEYWORDS:
        if valid in name_lower:
            return True
    
    # If name doesn't have any valid keywords, reject it
    return False


def calculate_hospital_score(hospital_name: str, condition: str) -> int:
    """Calculate relevance score for a hospital based on patient condition."""
    name_lower = hospital_name.lower()
    score = 0
    
    # +10 base score if it's clearly a hospital
    if "hospital" in name_lower:
        score += 10
    
    # +20 if multi-speciality (can handle many conditions)
    if any(kw in name_lower for kw in ["multi-speciality", "multispeciality", "multi-specialty", "multispecialty"]):
        score += 20
    
    # +50 if matches the patient's condition
    preferred_keywords = CONDITION_HOSPITAL_PREFERENCES.get(condition, [])
    for keyword in preferred_keywords:
        if keyword in name_lower:
            score += 50
            break  # Only add once
    
    # -30 penalty if contains unwanted keywords (but still passed filter)
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            score -= 30
            break
    
    return score


def get_hospital_match_tag(score: int, is_best: bool) -> str:
    """Get the display tag for a hospital based on its score."""
    if is_best and score >= 50:
        return "Best Match"
    elif score >= 30:
        return "Good Match"
    else:
        return "Nearby Option"


# =============================================================================
# MODELS
# =============================================================================

class TriageRequest(BaseModel):
    symptoms: str
    request_id: Optional[str] = None

class TriageResponse(BaseModel):
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
    condition_category: Optional[str] = None  # NEW: Include condition for frontend

class NearbyHospitalsRequest(BaseModel):
    lat: float
    lng: float
    symptoms: Optional[str] = None  # NEW: Optional symptoms for smart filtering

class HospitalInfo(BaseModel):
    name: str
    address: str
    distance: float
    distance_text: str
    lat: float
    lng: float
    place_id: Optional[str] = None
    score: int = 0  # Relevance score
    match_tag: str = "Nearby Option"  # Display tag
    phone: Optional[str] = None  # Phone number for calling
    is_open: Optional[bool] = None  # Whether hospital is currently open

class NearbyHospitalsResponse(BaseModel):
    success: bool
    hospitals: list[HospitalInfo]
    error: Optional[str] = None
    condition_category: Optional[str] = None  # NEW: Detected condition
    safety_message: Optional[str] = None  # NEW: Safety disclaimer

# =============================================================================
# SAFETY FILTER
# =============================================================================

BLOCKED_PATTERNS = [
    (r"\b(what|which)\s+(disease|condition|illness)\s+(do\s+)?i\s+have", "diagnosis_request"),
    (r"\bdiagnose\s+(me|my|this)", "diagnosis_request"),
    (r"\bdo\s+i\s+have\s+\w+\s*(disease|syndrome|cancer)?", "diagnosis_request"),
    (r"\bwhat\s+(medication|medicine|drug)s?\s+should\s+i\s+(take|use)", "medication_request"),
    (r"\b(prescribe|recommend)\s+(me\s+)?(medication|medicine)", "medication_request"),
    (r"\bhow\s+much\s+\w+\s+should\s+i\s+take", "medication_request"),
    (r"\b(dosage|dose)\s+(for|of)", "medication_request"),
]

SAFE_RESPONSES = {
    "diagnosis_request": {
        "message": "I cannot provide diagnoses. I can only assess symptom urgency.",
        "action": "Please describe your symptoms for triage assessment."
    },
    "medication_request": {
        "message": "I cannot recommend medications. A healthcare provider must do that.",
        "action": "I can help assess how urgently you need care."
    }
}

def check_input_safety(text: str) -> tuple[bool, Optional[str]]:
    """Check if input is safe. Returns (is_safe, block_reason)."""
    text_lower = text.lower()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, reason
    return True, None

# =============================================================================
# LLM PROMPT
# =============================================================================

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

# =============================================================================
# FASTAPI APP & RATE LIMITING
# =============================================================================

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered medical triage system with smart hospital recommendations"
)

# Apply rate limiter as middleware
app.state.limiter = limiter

# Custom exception handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return {
        "error": "Rate limit exceeded",
        "detail": str(exc.detail),
        "status": 429
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRIORITY_LABELS = {
    1: "CRITICAL",
    2: "URGENT",
    3: "SEMI-URGENT",
    4: "NON-URGENT"
}

DISCLAIMER = "This is a triage assessment only, not a medical diagnosis. A qualified healthcare professional must evaluate you."

@app.get("/")
async def root():
    """Serve frontend."""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "AI Triage API", "endpoints": ["/analyze", "/health", "/nearby-hospitals"]}

@app.get("/health")
@limiter.limit("100/minute")
async def health(request: Request):
    """
    Comprehensive health check endpoint.

    Returns detailed information about the system status, API keys, and uptime.
    """
    uptime = datetime.now() - START_TIME
    uptime_seconds = int(uptime.total_seconds())

    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
        "model": GROQ_MODEL,
        "api_keys": {
            "groq": "configured" if GROQ_API_KEY else "missing",
            "google_maps": "configured" if GOOGLE_MAPS_API_KEY else "missing"
        },
        "endpoints": {
            "analyze": "/analyze",
            "nearby_hospitals": "/nearby-hospitals",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.post("/analyze")
@limiter.limit("100/minute")
async def analyze(request: TriageRequest, req: Request) -> TriageResponse:
    """Analyze symptoms and return triage priority."""
    
    # Classify condition for hospital matching
    condition_category = classify_condition(request.symptoms)

    # Safety check
    is_safe, block_reason = check_input_safety(request.symptoms)
    if not is_safe:
        safe_response = SAFE_RESPONSES.get(block_reason, SAFE_RESPONSES["diagnosis_request"])
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
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
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
        return TriageResponse(
            priority=2,
            priority_label="URGENT",
            reason="System temporarily unavailable - defaulting to urgent for safety",
            action="Please seek immediate medical evaluation as a precaution",
            queue="urgent-care",
            confidence=0.0,
            escalation_triggers=["If symptoms worsen, call emergency services"],
            disclaimer=DISCLAIMER,
            condition_category=condition_category
        )
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        return TriageResponse(
            priority=2,
            priority_label="URGENT",
            reason="Unable to complete analysis - defaulting to urgent evaluation",
            action="Staff assessment required for proper evaluation",
            queue="urgent-care",
            confidence=0.0,
            escalation_triggers=["Any worsening symptoms"],
            disclaimer=DISCLAIMER,
            condition_category=condition_category
        )
    except httpx.TimeoutException:
        print("Request timeout")
        return TriageResponse(
            priority=2,
            priority_label="URGENT",
            reason="Analysis timed out - defaulting to urgent for your safety",
            action="Please try again or seek in-person evaluation",
            queue="urgent-care",
            confidence=0.0,
            escalation_triggers=["If symptoms are severe, seek immediate care"],
            disclaimer=DISCLAIMER,
            condition_category=condition_category
        )
    except Exception as e:
        print(f"Error: {e}")
        return TriageResponse(
            priority=2,
            priority_label="URGENT",
            reason="Server error occurred - defaulting to urgent for safety",
            action="Please try again. If issue persists, seek medical help directly.",
            queue="urgent-care",
            confidence=0.0,
            escalation_triggers=["Seek immediate care if symptoms are concerning"],
            disclaimer=DISCLAIMER,
            condition_category=condition_category
        )

# =============================================================================
# NEARBY HOSPITALS ENDPOINT (with Smart Filtering & Scoring)
# =============================================================================

@app.post("/nearby-hospitals", response_model=NearbyHospitalsResponse)
@limiter.limit("100/minute")
async def nearby_hospitals(request: NearbyHospitalsRequest, req: Request):
    """Find nearby hospitals with smart filtering and condition-based scoring."""

    # Validate coordinates
    if not (-90 <= request.lat <= 90) or not (-180 <= request.lng <= 180):
        return NearbyHospitalsResponse(
            success=False,
            hospitals=[],
            error="Invalid coordinates provided"
        )

    # Classify patient condition if symptoms provided
    condition = classify_condition(request.symptoms) if request.symptoms else "OTHER"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                GOOGLE_PLACES_URL,
                params={
                    "location": f"{request.lat},{request.lng}",
                    "radius": HOSPITAL_SEARCH_RADIUS,
                    "type": "hospital",
                    "key": GOOGLE_MAPS_API_KEY
                }
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                error_msg = data.get("error_message", data.get("status", "Unknown error"))
                print(f"Google Places API error: {error_msg}")
                return NearbyHospitalsResponse(
                    success=False,
                    hospitals=[],
                    error=f"Google Places API: {error_msg}"
                )

            results = data.get("results", [])
            if not results:
                return NearbyHospitalsResponse(
                    success=True,
                    hospitals=[],
                    error="No hospitals found within 5km",
                    condition_category=condition
                )

            # STEP 1: Filter out invalid places (diagnostic centers, labs, etc.)
            valid_hospitals = []
            for place in results:
                name = place.get("name", "")
                if is_valid_hospital(name):
                    valid_hospitals.append(place)
                else:
                    print(f"Filtered out: {name}")

            # If no valid hospitals after filtering, use all results with warning
            safety_message = None
            if not valid_hospitals:
                valid_hospitals = results
                safety_message = "Showing nearest available hospitals. Please confirm with medical professionals."

            # STEP 2 & 3: Score and process hospitals
            hospitals = []
            for place in valid_hospitals[:15]:  # Process up to 15 results
                place_lat = place["geometry"]["location"]["lat"]
                place_lng = place["geometry"]["location"]["lng"]
                distance = haversine_distance(
                    request.lat, request.lng,
                    place_lat, place_lng
                )
                
                name = place.get("name", "Unknown Hospital")
                score = calculate_hospital_score(name, condition)
                
                # Check if open
                is_open = place.get("opening_hours", {}).get("open_now")

                hospitals.append(HospitalInfo(
                    name=name,
                    address=place.get("vicinity", "Address not available"),
                    distance=distance,
                    distance_text=f"{distance} km",
                    lat=place_lat,
                    lng=place_lng,
                    place_id=place.get("place_id"),
                    score=score,
                    match_tag="Nearby Option",  # Will be updated after sorting
                    is_open=is_open
                ))

            # STEP 4: Sort by score (descending), then by distance (ascending)
            hospitals.sort(key=lambda h: (-h.score, h.distance))

            # STEP 5: Assign match tags
            if hospitals:
                hospitals[0].match_tag = get_hospital_match_tag(hospitals[0].score, is_best=True)
                for h in hospitals[1:]:
                    h.match_tag = get_hospital_match_tag(h.score, is_best=False)

            # Return top 5 hospitals
            top_hospitals = hospitals[:5]
            
            # STEP 6: Fetch phone numbers for top hospitals (Place Details API)
            for hospital in top_hospitals:
                if hospital.place_id:
                    try:
                        details_response = await client.get(
                            GOOGLE_PLACE_DETAILS_URL,
                            params={
                                "place_id": hospital.place_id,
                                "fields": "formatted_phone_number",
                                "key": GOOGLE_MAPS_API_KEY
                            }
                        )
                        details_data = details_response.json()
                        if details_data.get("status") == "OK":
                            hospital.phone = details_data.get("result", {}).get("formatted_phone_number")
                    except Exception as e:
                        print(f"Error fetching phone for {hospital.name}: {e}")

            print(f"Found {len(top_hospitals)} relevant hospitals for condition: {condition}")
            for h in top_hospitals:
                print(f"  - {h.name} (score: {h.score}, distance: {h.distance}km, tag: {h.match_tag}, phone: {h.phone})")

            return NearbyHospitalsResponse(
                success=True,
                hospitals=top_hospitals,
                condition_category=condition,
                safety_message=safety_message
            )

    except httpx.TimeoutException:
        print("Google Places API timeout")
        return NearbyHospitalsResponse(
            success=False,
            hospitals=[],
            error="Request timed out. Please try again."
        )
    except httpx.HTTPStatusError as e:
        print(f"Google Places API HTTP error: {e}")
        return NearbyHospitalsResponse(
            success=False,
            hospitals=[],
            error="Failed to fetch hospital data"
        )
    except Exception as e:
        print(f"Nearby hospitals error: {e}")
        return NearbyHospitalsResponse(
            success=False,
            hospitals=[],
            error="An error occurred while finding hospitals"
        )

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    print(f"\n{'='*60}")
    print(f"🏥 {APP_NAME} v{APP_VERSION}")
    print(f"{'='*60}")
    print(f"Model: {GROQ_MODEL}")
    print(f"Groq API Key: {'✓ Set' if GROQ_API_KEY else '✗ NOT SET'}")
    print(f"Google Maps Key: {'✓ Set' if GOOGLE_MAPS_API_KEY else '✗ NOT SET'}")
    print(f"Rate Limiting: 100 requests/minute per IP")
    print(f"{'='*60}\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)
