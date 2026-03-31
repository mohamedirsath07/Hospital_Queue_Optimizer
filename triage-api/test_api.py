"""Test examples for the triage API."""

import httpx

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint."""
    response = httpx.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())


def test_critical_symptoms():
    """Test critical symptom detection (bypasses LLM)."""
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "symptoms": "I have severe chest pain radiating to my left arm and I can't breathe",
            "request_id": "test-critical-001",
        },
    )
    print("\n=== CRITICAL SYMPTOMS ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Priority: {data['priority']} ({data['priority_label']})")
    print(f"Reason: {data['reason']}")
    print(f"Action: {data['action']}")
    print(f"Queue: {data['queue']}")
    print(f"Safety Flags: {[f['code'] for f in data['safety_flags']]}")


def test_moderate_symptoms():
    """Test moderate symptoms (uses LLM)."""
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "symptoms": "I have a headache and feel nauseous. Started this morning.",
            "vital_signs": {"temperature_celsius": 37.8},
            "patient_context": {"age": 35},
            "request_id": "test-moderate-001",
        },
    )
    print("\n=== MODERATE SYMPTOMS ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Priority: {data['priority']} ({data['priority_label']})")
    print(f"Reason: {data['reason']}")
    print(f"Action: {data['action']}")
    print(f"Queue: {data['queue']}")
    print(f"Confidence: {data['confidence']}")
    print(f"Escalation Triggers: {data['escalation_triggers']}")


def test_minor_symptoms():
    """Test minor symptoms."""
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "symptoms": "I have a small paper cut on my finger",
            "request_id": "test-minor-001",
        },
    )
    print("\n=== MINOR SYMPTOMS ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Priority: {data['priority']} ({data['priority_label']})")
    print(f"Reason: {data['reason']}")


def test_mental_health_crisis():
    """Test mental health crisis detection."""
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "symptoms": "I've been thinking about hurting myself. I don't want to live anymore.",
            "request_id": "test-mental-001",
        },
    )
    print("\n=== MENTAL HEALTH CRISIS ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Priority: {data['priority']} ({data['priority_label']})")
    print(f"Safety Flags: {[f['code'] for f in data['safety_flags']]}")


def test_pediatric_high_risk():
    """Test pediatric high-risk case."""
    response = httpx.post(
        f"{BASE_URL}/analyze",
        json={
            "symptoms": "My baby has a high fever and won't stop crying",
            "patient_context": {"age": 0},
            "request_id": "test-peds-001",
        },
    )
    print("\n=== PEDIATRIC HIGH RISK ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Priority: {data['priority']} ({data['priority_label']})")


if __name__ == "__main__":
    print("Running Triage API Tests")
    print("=" * 50)

    test_health()
    test_critical_symptoms()
    test_moderate_symptoms()
    test_minor_symptoms()
    test_mental_health_crisis()
    test_pediatric_high_risk()

    print("\n" + "=" * 50)
    print("Tests complete!")
