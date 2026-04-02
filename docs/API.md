# API Documentation

## Overview

The AI Hospital Triage System provides RESTful APIs for symptom analysis and hospital search.

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

Currently, the API does not require authentication. API keys for external services (Groq, Google Maps) are configured server-side.

## Endpoints

### 1. Symptom Analysis

**Endpoint:** `POST /api/v1/analyze`

Analyzes patient symptoms and returns a triage priority classification.

#### Request

```json
{
  "symptoms": "string (required)",
  "request_id": "string (optional)"
}
```

#### Response

```json
{
  "priority": 1,
  "priority_label": "CRITICAL",
  "reason": "Brief symptom summary",
  "action": "Recommended action for staff",
  "queue": "critical-care",
  "confidence": 0.95,
  "escalation_triggers": ["List of warning signs"],
  "disclaimer": "Medical disclaimer text",
  "blocked": false,
  "blocked_reason": null,
  "condition_category": "CARDIAC"
}
```

#### Priority Levels

| Priority | Label | Description |
|----------|-------|-------------|
| 1 | CRITICAL | Life-threatening, immediate attention |
| 2 | URGENT | Serious, needs prompt attention |
| 3 | SEMI-URGENT | Needs attention within 1 hour |
| 4 | NON-URGENT | Minor, can wait |

### 2. Nearby Hospitals

**Endpoint:** `POST /api/v1/nearby-hospitals`

Finds hospitals near the user's location with condition-based matching.

#### Request

```json
{
  "lat": 13.0827,
  "lng": 80.2707,
  "symptoms": "string (optional)"
}
```

#### Response

```json
{
  "success": true,
  "hospitals": [
    {
      "name": "Apollo Hospital",
      "address": "123 Main Street",
      "distance": 2.5,
      "distance_text": "2.5 km",
      "lat": 13.0850,
      "lng": 80.2750,
      "place_id": "ChIJ...",
      "score": 70,
      "match_tag": "Best Match",
      "phone": "+91 44 1234 5678",
      "is_open": true
    }
  ],
  "error": null,
  "condition_category": "CARDIAC",
  "safety_message": null
}
```

### 3. Health Check

**Endpoint:** `GET /health`

Returns the server health status.

#### Response

```json
{
  "status": "ok",
  "model": "llama-3.3-70b-versatile",
  "version": "1.0.0"
}
```

## Error Handling

All errors return a structured response:

```json
{
  "detail": "Error description"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Rate Limits

- Groq API: Depends on your Groq plan
- Google Places API: Depends on your Google Cloud quota

## Interactive Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
