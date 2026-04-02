"""
Hospital Service
Handles finding and scoring nearby hospitals.
"""

import math
import httpx
from typing import Optional

from ..core.config import get_settings
from ..core.constants import (
    EXCLUDED_KEYWORDS, 
    VALID_HOSPITAL_KEYWORDS,
    CONDITION_HOSPITAL_PREFERENCES
)
from ..models.schemas import NearbyHospitalsRequest, NearbyHospitalsResponse, HospitalInfo
from .triage_service import classify_condition


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def is_valid_hospital(name: str) -> bool:
    """
    Check if a place is a valid hospital (not a diagnostic center/lab).
    
    Args:
        name: Place name to check
        
    Returns:
        True if valid hospital, False otherwise
    """
    name_lower = name.lower()
    
    # First, check if it contains excluded keywords
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            if "hospital" not in name_lower:
                return False
    
    # Check if it contains at least one valid hospital keyword
    for valid in VALID_HOSPITAL_KEYWORDS:
        if valid in name_lower:
            return True
    
    return False


def calculate_hospital_score(hospital_name: str, condition: str) -> int:
    """
    Calculate relevance score for a hospital based on patient condition.
    
    Args:
        hospital_name: Name of the hospital
        condition: Patient condition category
        
    Returns:
        Relevance score (higher is better)
    """
    name_lower = hospital_name.lower()
    score = 0
    
    # +10 base score if it's clearly a hospital
    if "hospital" in name_lower:
        score += 10
    
    # +20 if multi-speciality
    if any(kw in name_lower for kw in ["multi-speciality", "multispeciality", "multi-specialty", "multispecialty"]):
        score += 20
    
    # +50 if matches the patient's condition
    preferred_keywords = CONDITION_HOSPITAL_PREFERENCES.get(condition, [])
    for keyword in preferred_keywords:
        if keyword in name_lower:
            score += 50
            break
    
    # -30 penalty if contains unwanted keywords
    for excluded in EXCLUDED_KEYWORDS:
        if excluded in name_lower:
            score -= 30
            break
    
    return score


def get_hospital_match_tag(score: int, is_best: bool) -> str:
    """
    Get the display tag for a hospital based on its score.
    
    Args:
        score: Hospital relevance score
        is_best: Whether this is the best match
        
    Returns:
        Display tag string
    """
    if is_best and score >= 50:
        return "Best Match"
    elif score >= 30:
        return "Good Match"
    else:
        return "Nearby Option"


async def find_nearby_hospitals(request: NearbyHospitalsRequest) -> NearbyHospitalsResponse:
    """
    Find nearby hospitals with smart filtering and condition-based scoring.
    
    Args:
        request: NearbyHospitalsRequest with coordinates and optional symptoms
        
    Returns:
        NearbyHospitalsResponse with sorted hospital list
    """
    settings = get_settings()
    
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
                settings.GOOGLE_PLACES_URL,
                params={
                    "location": f"{request.lat},{request.lng}",
                    "radius": settings.HOSPITAL_SEARCH_RADIUS,
                    "type": "hospital",
                    "key": settings.GOOGLE_MAPS_API_KEY
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
            
            # Filter out invalid places
            valid_hospitals = [place for place in results if is_valid_hospital(place.get("name", ""))]
            
            safety_message = None
            if not valid_hospitals:
                valid_hospitals = results
                safety_message = "Showing nearest available hospitals. Please confirm with medical professionals."
            
            # Score and process hospitals
            hospitals = []
            for place in valid_hospitals[:15]:
                place_lat = place["geometry"]["location"]["lat"]
                place_lng = place["geometry"]["location"]["lng"]
                distance = haversine_distance(request.lat, request.lng, place_lat, place_lng)
                
                name = place.get("name", "Unknown Hospital")
                score = calculate_hospital_score(name, condition)
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
                    match_tag="Nearby Option",
                    is_open=is_open
                ))
            
            # Sort by score (descending), then by distance (ascending)
            hospitals.sort(key=lambda h: (-h.score, h.distance))
            
            # Assign match tags
            if hospitals:
                hospitals[0].match_tag = get_hospital_match_tag(hospitals[0].score, is_best=True)
                for h in hospitals[1:]:
                    h.match_tag = get_hospital_match_tag(h.score, is_best=False)
            
            # Get top 5 and fetch phone numbers
            top_hospitals = hospitals[:5]
            
            for hospital in top_hospitals:
                if hospital.place_id:
                    try:
                        details_response = await client.get(
                            settings.GOOGLE_PLACE_DETAILS_URL,
                            params={
                                "place_id": hospital.place_id,
                                "fields": "formatted_phone_number",
                                "key": settings.GOOGLE_MAPS_API_KEY
                            }
                        )
                        details_data = details_response.json()
                        if details_data.get("status") == "OK":
                            hospital.phone = details_data.get("result", {}).get("formatted_phone_number")
                    except Exception as e:
                        print(f"Error fetching phone for {hospital.name}: {e}")
            
            print(f"Found {len(top_hospitals)} relevant hospitals for condition: {condition}")
            
            return NearbyHospitalsResponse(
                success=True,
                hospitals=top_hospitals,
                condition_category=condition,
                safety_message=safety_message
            )
            
    except httpx.TimeoutException:
        return NearbyHospitalsResponse(success=False, hospitals=[], error="Request timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        print(f"Google Places API HTTP error: {e}")
        return NearbyHospitalsResponse(success=False, hospitals=[], error="Failed to fetch hospital data")
    except Exception as e:
        print(f"Nearby hospitals error: {e}")
        return NearbyHospitalsResponse(success=False, hospitals=[], error="An error occurred while finding hospitals")
