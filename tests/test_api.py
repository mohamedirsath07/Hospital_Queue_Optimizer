"""
Test suite for AI Hospital Triage System

Run with:
    pytest -v
    pytest tests/test_api.py -v
    pytest --cov=. tests/
"""

import pytest
from fastapi.testclient import TestClient
from main import app, classify_condition, is_valid_hospital, calculate_hospital_score

# Create test client
client = TestClient(app)


# ============================================================================
# HEALTH ENDPOINT TESTS
# ============================================================================

def test_health_endpoint_status():
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_fields():
    """Test health check endpoint response has required fields."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert "model" in data
    assert "api_keys" in data
    assert "endpoints" in data


def test_health_endpoint_api_keys():
    """Test health check reports API key configuration."""
    response = client.get("/health")
    data = response.json()

    # Should have api_keys object
    assert "groq" in data["api_keys"]
    assert "google_maps" in data["api_keys"]

    # Should be either "configured" or "missing"
    assert data["api_keys"]["groq"] in ["configured", "missing"]
    assert data["api_keys"]["google_maps"] in ["configured", "missing"]


# ============================================================================
# ROOT ENDPOINT TESTS
# ============================================================================

def test_root_endpoint():
    """Test root endpoint returns 200."""
    response = client.get("/")
    assert response.status_code == 200


# ============================================================================
# SYMPTOM ANALYSIS ENDPOINT TESTS
# ============================================================================

def test_analyze_empty_symptoms():
    """Test analyzing empty symptom string."""
    response = client.post("/analyze", json={"symptoms": ""})
    assert response.status_code == 422  # Validation error


def test_analyze_valid_symptoms():
    """Test analyzing valid symptoms."""
    response = client.post("/analyze", json={"symptoms": "mild headache"})
    assert response.status_code == 200

    data = response.json()
    assert "priority" in data
    assert "priority_label" in data
    assert 1 <= data["priority"] <= 4


def test_analyze_response_structure():
    """Test analyze endpoint response has all required fields."""
    response = client.post(
        "/analyze",
        json={"symptoms": "chest pain"}
    )
    assert response.status_code == 200

    data = response.json()

    # Check all required fields
    assert "priority" in data
    assert "priority_label" in data
    assert "reason" in data
    assert "action" in data
    assert "queue" in data
    assert "confidence" in data
    assert "escalation_triggers" in data
    assert "disclaimer" in data
    assert "blocked" in data
    assert "condition_category" in data

    # Check field types
    assert isinstance(data["priority"], int)
    assert isinstance(data["priority_label"], str)
    assert isinstance(data["reason"], str)
    assert isinstance(data["action"], str)
    assert isinstance(data["queue"], str)
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["escalation_triggers"], list)
    assert isinstance(data["disclaimer"], str)
    assert isinstance(data["blocked"], bool)
    assert isinstance(data["condition_category"], str)


def test_analyze_critical_condition():
    """Test analyzing critical condition."""
    response = client.post(
        "/analyze",
        json={"symptoms": "chest pain and shortness of breath"}
    )
    assert response.status_code == 200

    data = response.json()
    # Should be high priority (1 or 2)
    assert data["priority"] <= 2
    assert data["condition_category"] == "CARDIAC"


def test_analyze_non_urgent_condition():
    """Test analyzing non-urgent condition."""
    response = client.post(
        "/analyze",
        json={"symptoms": "very mild headache"}
    )
    assert response.status_code == 200

    data = response.json()
    # Should be lower priority
    assert data["priority"] >= 3


def test_analyze_with_request_id():
    """Test analyze with optional request_id field."""
    response = client.post(
        "/analyze",
        json={
            "symptoms": "mild pain",
            "request_id": "test-123"
        }
    )
    assert response.status_code == 200
    assert response.json()["priority"] in [1, 2, 3, 4]


def test_analyze_blocked_diagnosis_request():
    """Test that diagnosis requests are blocked."""
    response = client.post(
        "/analyze",
        json={"symptoms": "What disease do I have?"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["blocked"] is True
    assert data["blocked_reason"] is not None


def test_analyze_blocked_medication_request():
    """Test that medication requests are blocked."""
    response = client.post(
        "/analyze",
        json={"symptoms": "What medicine should I take?"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["blocked"] is True
    assert "medication" in data["blocked_reason"].lower()


def test_analyze_confidence_score():
    """Test that confidence score is between 0 and 1."""
    response = client.post(
        "/analyze",
        json={"symptoms": "severe fever"}
    )
    assert response.status_code == 200

    data = response.json()
    assert 0.0 <= data["confidence"] <= 1.0


# ============================================================================
# NEARBY HOSPITALS ENDPOINT TESTS
# ============================================================================

def test_nearby_hospitals_invalid_latitude():
    """Test nearby hospitals with invalid latitude."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 200, "lng": 80}  # Invalid latitude
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert "Invalid" in data["error"]


def test_nearby_hospitals_invalid_longitude():
    """Test nearby hospitals with invalid longitude."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 13, "lng": 400}  # Invalid longitude
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is False
    assert "Invalid" in data["error"]


def test_nearby_hospitals_valid_coordinates():
    """Test nearby hospitals with valid coordinates."""
    response = client.post(
        "/nearby-hospitals",
        json={
            "lat": 13.0827,
            "lng": 80.2707,
            "symptoms": "chest pain"
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert "success" in data
    assert "hospitals" in data
    assert "condition_category" in data


def test_nearby_hospitals_response_structure():
    """Test nearby hospitals response structure."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 13.0827, "lng": 80.2707}
    )
    assert response.status_code == 200

    data = response.json()

    # Check response structure
    assert isinstance(data["success"], bool)
    assert isinstance(data["hospitals"], list)
    assert isinstance(data["condition_category"], (str, type(None)))

    # If hospitals found, check structure
    if data["hospitals"]:
        hospital = data["hospitals"][0]
        assert "name" in hospital
        assert "address" in hospital
        assert "distance" in hospital
        assert "distance_text" in hospital
        assert "lat" in hospital
        assert "lng" in hospital
        assert "score" in hospital
        assert "match_tag" in hospital


def test_nearby_hospitals_max_results():
    """Test that nearby hospitals returns max 5 results."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 13.0827, "lng": 80.2707}
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["hospitals"]) <= 5


def test_nearby_hospitals_with_symptoms():
    """Test nearby hospitals with symptom classification."""
    response = client.post(
        "/nearby-hospitals",
        json={
            "lat": 13.0827,
            "lng": 80.2707,
            "symptoms": "chest pain"
        }
    )
    assert response.status_code == 200

    data = response.json()
    if data["hospitals"]:
        # Condition should be detected
        assert data["condition_category"] == "CARDIAC"


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_classify_condition_cardiac():
    """Test condition classification for cardiac symptoms."""
    condition = classify_condition("chest pain and shortness of breath")
    assert condition == "CARDIAC"


def test_classify_condition_trauma():
    """Test condition classification for trauma."""
    condition = classify_condition("bleeding from injury")
    assert condition == "TRAUMA"


def test_classify_condition_neuro():
    """Test condition classification for neuro."""
    condition = classify_condition("seizure and unconsciousness")
    assert condition == "NEURO"


def test_classify_condition_general():
    """Test condition classification for general."""
    condition = classify_condition("high fever and cough")
    assert condition == "GENERAL"


def test_classify_condition_unknown():
    """Test condition classification returns OTHER for unknown."""
    condition = classify_condition("xyz abc defghij")
    assert condition == "OTHER"


def test_is_valid_hospital_true():
    """Test hospital validation returns True for valid hospitals."""
    assert is_valid_hospital("Apollo Hospital") is True
    assert is_valid_hospital("General Hospital") is True
    assert is_valid_hospital("Trauma Center") is True
    assert is_valid_hospital("Multi-speciality Hospital") is True


def test_is_valid_hospital_false():
    """Test hospital validation returns False for non-hospitals."""
    assert is_valid_hospital("Diagnostic Center") is False
    assert is_valid_hospital("Pathology Lab") is False
    assert is_valid_hospital("Pharmacy") is False
    assert is_valid_hospital("Dental Clinic") is False


def test_calculate_hospital_score():
    """Test hospital scoring algorithm."""
    # General hospital (low score)
    score1 = calculate_hospital_score("General Hospital", "CARDIAC")

    # Cardiac hospital (high score)
    score2 = calculate_hospital_score("Cardiac Center", "CARDIAC")

    # Cardiac hospital should score higher for CARDIAC condition
    assert score2 > score1


def test_calculate_hospital_score_multispecialty():
    """Test hospital scoring gives bonus for multi-specialty."""
    score1 = calculate_hospital_score("Hospital", "GENERAL")
    score2 = calculate_hospital_score("Multi-speciality Hospital", "GENERAL")

    # Multi-specialty should score higher
    assert score2 > score1


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_analyze_missing_symptoms_field():
    """Test analyze endpoint requires symptoms field."""
    response = client.post("/analyze", json={})
    assert response.status_code == 422  # Validation error


def test_nearby_hospitals_missing_lat():
    """Test nearby hospitals requires lat field."""
    response = client.post(
        "/nearby-hospitals",
        json={"lng": 80}
    )
    assert response.status_code == 422  # Validation error


def test_nearby_hospitals_missing_lng():
    """Test nearby hospitals requires lng field."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 13}
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_analyze_very_long_symptoms():
    """Test analyze with very long symptom description."""
    long_symptoms = "pain " * 500  # Very long string
    response = client.post(
        "/analyze",
        json={"symptoms": long_symptoms}
    )
    # Should still process (or timeout gracefully)
    assert response.status_code in [200, 500, 504]


def test_analyze_special_characters():
    """Test analyze with special characters."""
    response = client.post(
        "/analyze",
        json={"symptoms": "headache !@#$%^&*()"}
    )
    assert response.status_code == 200


def test_nearby_hospitals_boundary_coordinates():
    """Test nearby hospitals with boundary coordinates."""
    # Test valid boundary values
    response = client.post(
        "/nearby-hospitals",
        json={"lat": -90, "lng": -180}  # South pole, international dateline
    )
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
