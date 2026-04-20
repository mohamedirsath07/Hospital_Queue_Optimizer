# API Documentation

Complete reference for all endpoints, request/response formats, and error codes for the AI Hospital Triage System.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Rate Limiting](#rate-limiting)
5. [Endpoints](#endpoints)
6. [Error Codes](#error-codes)
7. [Examples](#examples)
8. [Interactive Documentation](#interactive-documentation)

---

## Overview

The AI Hospital Triage System provides RESTful APIs for:

- **Symptom Analysis:** Classify patient urgency using AI
- **Hospital Search:** Find nearby hospitals with condition matching
- **Health Monitoring:** Check system status

All endpoints return JSON responses. The API uses standard HTTP status codes.

---

## Base URL

| Environment | URL |
|-------------|-----|
| Local Development | `http://127.0.0.1:8000` |
| Render | `https://your-app.onrender.com` |
| Vercel | `https://your-app.vercel.app` |

---

## Authentication

**Current Status:** No authentication required

The API does not require authentication tokens. API keys for external services (Groq, Google Maps) are configured server-side and secured via environment variables.

**Future:** Authentication may be added for production deployments.

---

## Rate Limiting

Rate limiting is enforced to prevent abuse and ensure fair resource usage.

### Limits

| Endpoint | Limit |
|----------|-------|
| All endpoints | 100 requests/minute per IP |
| General limit | 1000 requests/hour per IP |

### Rate Limit Headers

All responses include rate limit information:

```
RateLimit-Limit: 100
RateLimit-Remaining: 99
RateLimit-Reset: 1234567890
```

### Rate Limit Exceeded Response

**Status Code:** 429 Too Many Requests

```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests",
  "status": 429
}
```

---

## Endpoints

### 1. Symptom Analysis

Analyzes patient symptoms and returns triage priority classification.

#### Request

**Endpoint:** `POST /analyze`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "symptoms": "Severe chest pain radiating to left arm, shortness of breath",
  "request_id": "optional-unique-id-for-tracking"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| symptoms | string | Yes | Patient symptom description |
| request_id | string | No | Unique ID for tracking/logging |

#### Response

**Status Code:** 200 OK

**Body:**
```json
{
  "priority": 1,
  "priority_label": "CRITICAL",
  "reason": "Chest pain with radiation and breathing difficulty",
  "action": "Immediate cardiac evaluation required",
  "queue": "critical-care",
  "confidence": 0.95,
  "escalation_triggers": ["Loss of consciousness", "Increasing pain"],
  "disclaimer": "This is a triage assessment only, not a medical diagnosis...",
  "blocked": false,
  "blocked_reason": null,
  "condition_category": "CARDIAC"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| priority | integer | Urgency level (1-4) |
| priority_label | string | Human-readable priority |
| reason | string | Symptom summary without diagnosis |
| action | string | Recommended action for staff |
| queue | string | Triage queue assignment |
| confidence | float | Confidence score (0.0-1.0) |
| escalation_triggers | array | Warning signs to monitor |
| disclaimer | string | Medical disclaimer |
| blocked | boolean | Whether request was blocked by safety filter |
| blocked_reason | string | Reason for blocking (if applicable) |
| condition_category | string | Detected condition category |

#### Priority Levels

| Priority | Label | Description | Expected Wait |
|----------|-------|-------------|----------------|
| 1 | CRITICAL | Life-threatening, immediate attention | <5 minutes |
| 2 | URGENT | Serious, needs prompt attention | <30 minutes |
| 3 | SEMI-URGENT | Needs attention within 1 hour | <1 hour |
| 4 | NON-URGENT | Minor, can wait | <4 hours |

#### Condition Categories

| Category | Examples |
|----------|----------|
| CARDIAC | Chest pain, shortness of breath, palpitations |
| TRAUMA | Injuries, bleeding, fractures, burns |
| NEURO | Seizures, stroke, loss of consciousness |
| GENERAL | Fever, infection, pain, weakness |
| OTHER | Unclassified conditions |

#### Queue Types

- `critical-care` - Immediate care required
- `urgent-care` - Prompt attention needed
- `standard-care` - Routine care (within 1 hour)
- `routine` - Non-urgent care

#### Examples

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "Sudden severe headache with neck stiffness and fever"
  }'
```

**Response (Critical):**
```json
{
  "priority": 1,
  "priority_label": "CRITICAL",
  "reason": "Severe headache with neck stiffness and fever",
  "action": "Immediate neurological evaluation",
  "queue": "critical-care",
  "confidence": 0.92,
  "escalation_triggers": ["Loss of consciousness", "Convulsions"],
  "condition_category": "NEURO"
}
```

**Response (Non-Urgent):**
```json
{
  "priority": 4,
  "priority_label": "NON-URGENT",
  "reason": "Mild tension headache",
  "action": "Standard care, monitor symptoms",
  "queue": "routine",
  "confidence": 0.85,
  "escalation_triggers": [],
  "condition_category": "GENERAL"
}
```

---

### 2. Nearby Hospitals

Finds hospitals near the user's location with condition-based matching and scoring.

#### Request

**Endpoint:** `POST /nearby-hospitals`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "lat": 13.0827,
  "lng": 80.2707,
  "symptoms": "chest pain"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| lat | float | Yes | Latitude (-90 to 90) |
| lng | float | Yes | Longitude (-180 to 180) |
| symptoms | string | No | Patient symptoms for smart filtering |

#### Response

**Status Code:** 200 OK

**Body:**
```json
{
  "success": true,
  "hospitals": [
    {
      "name": "Apollo Hospital",
      "address": "123 Main Street, Chennai",
      "distance": 2.5,
      "distance_text": "2.5 km",
      "lat": 13.0850,
      "lng": 80.2750,
      "place_id": "ChIJ...",
      "score": 85,
      "match_tag": "Best Match",
      "phone": "+91 44 1234 5678",
      "is_open": true
    },
    {
      "name": "Fortis Hospital",
      "address": "456 Second Street",
      "distance": 3.8,
      "distance_text": "3.8 km",
      "lat": 13.0900,
      "lng": 80.2800,
      "place_id": "ChIJ...",
      "score": 70,
      "match_tag": "Good Match",
      "phone": "+91 44 8765 4321",
      "is_open": true
    }
  ],
  "error": null,
  "condition_category": "CARDIAC",
  "safety_message": null
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether search was successful |
| hospitals | array | List of hospitals (max 5) |
| error | string | Error message (if any) |
| condition_category | string | Detected condition from symptoms |
| safety_message | string | Warning if results not fully filtered |

**Hospital Object Fields:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Hospital name |
| address | string | Address/vicinity |
| distance | float | Distance in kilometers |
| distance_text | string | Formatted distance |
| lat | float | Latitude coordinate |
| lng | float | Longitude coordinate |
| place_id | string | Google Places ID |
| score | integer | Relevance score (0-100) |
| match_tag | string | "Best Match", "Good Match", or "Nearby Option" |
| phone | string | Hospital phone number |
| is_open | boolean | Currently open status |

#### Scoring Algorithm

Hospitals are scored based on:

1. **Base Score:** 10 points if it's clearly a hospital
2. **Specialization:** +20 for multi-speciality hospitals
3. **Condition Match:** +50 if matches patient condition
4. **Penalties:** -30 if contains unwanted keywords

Results sorted by score (descending), then distance (ascending).

#### Examples

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/nearby-hospitals \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 13.0827,
    "lng": 80.2707,
    "symptoms": "chest pain"
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "hospitals": [
    {
      "name": "Cardiac Care Hospital",
      "address": "Main Road, Chennai",
      "distance": 1.2,
      "distance_text": "1.2 km",
      "lat": 13.0850,
      "lng": 80.2750,
      "place_id": "ChIJ...",
      "score": 95,
      "match_tag": "Best Match",
      "phone": "+91 44 1111 1111",
      "is_open": true
    }
  ],
  "error": null,
  "condition_category": "CARDIAC",
  "safety_message": null
}
```

**Response (No Results):**
```json
{
  "success": true,
  "hospitals": [],
  "error": "No hospitals found within 5km",
  "condition_category": "GENERAL"
}
```

---

### 3. Health Check

Returns detailed system status and availability information.

#### Request

**Endpoint:** `GET /health`

**Headers:** None required

#### Response

**Status Code:** 200 OK

**Body:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2026-04-20T10:30:45.123456",
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m 0s",
  "model": "llama-3.3-70b-versatile",
  "api_keys": {
    "groq": "configured",
    "google_maps": "configured"
  },
  "endpoints": {
    "analyze": "/analyze",
    "nearby_hospitals": "/nearby-hospitals",
    "docs": "/docs",
    "redoc": "/redoc"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | System health status |
| version | string | API version |
| timestamp | string | ISO 8601 timestamp |
| uptime_seconds | integer | Seconds since startup |
| uptime_formatted | string | Human-readable uptime |
| model | string | AI model name |
| api_keys | object | Configuration status of API keys |
| endpoints | object | Available endpoint URLs |

#### Examples

**Request:**
```bash
curl http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2026-04-20T10:30:45.123456",
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m 0s",
  "model": "llama-3.3-70b-versatile",
  "api_keys": {
    "groq": "configured",
    "google_maps": "configured"
  },
  "endpoints": {
    "analyze": "/analyze",
    "nearby_hospitals": "/nearby-hospitals",
    "docs": "/docs",
    "redoc": "/redoc"
  }
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Description | Cause |
|------|-------------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format |
| 422 | Validation Error | Invalid field values |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | External API unavailable |

### Error Response Format

```json
{
  "detail": "Error description"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "symptoms"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Common Error Scenarios

**Missing Required Field:**
```json
{
  "detail": [
    {
      "loc": ["body", "symptoms"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
Status: 422

**Invalid Coordinates:**
```json
{
  "success": false,
  "hospitals": [],
  "error": "Invalid coordinates provided"
}
```
Status: 200 (wrapped in response model)

**Rate Limit Exceeded:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests",
  "status": 429
}
```
Status: 429

**API Service Down:**
```json
{
  "priority": 2,
  "priority_label": "URGENT",
  "reason": "System temporarily unavailable",
  "action": "Please seek immediate medical evaluation",
  "queue": "urgent-care",
  "confidence": 0.0
}
```
Status: 200 (defaults to URGENT for safety)

---

## Examples

### Complete Workflow

**1. Analyze Symptoms:**

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "chest pain and shortness of breath"
  }'
```

Response:
```json
{
  "priority": 1,
  "priority_label": "CRITICAL",
  "condition_category": "CARDIAC"
}
```

**2. Find Nearby Hospitals:**

```bash
curl -X POST http://127.0.0.1:8000/nearby-hospitals \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 13.0827,
    "lng": 80.2707,
    "symptoms": "chest pain and shortness of breath"
  }'
```

Response:
```json
{
  "success": true,
  "hospitals": [
    {
      "name": "Cardiac Care Hospital",
      "distance": 1.2,
      "match_tag": "Best Match",
      "phone": "+91 44 1234 5678"
    }
  ],
  "condition_category": "CARDIAC"
}
```

**3. Check System Health:**

```bash
curl http://127.0.0.1:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "api_keys": {
    "groq": "configured",
    "google_maps": "configured"
  }
}
```

---

## Interactive Documentation

The API includes interactive documentation:

- **Swagger UI:** `/docs`
  - Try out endpoints
  - View schemas
  - See live responses

- **ReDoc:** `/redoc`
  - Alternative documentation format
  - Better for reading
  - Responsive design

---

## Best Practices

### Request Handling

1. **Always include Content-Type header** for POST requests
2. **Validate input data** before sending
3. **Handle rate limits** gracefully (implement exponential backoff)
4. **Use HTTPS** in production

### Response Handling

1. **Check status code** before processing response
2. **Parse JSON** carefully (handle network errors)
3. **Implement error logging** for debugging
4. **Handle network timeouts** (30 second max)

### Error Handling Example

```python
import httpx
import json

async def analyze_symptoms(symptoms: str):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://127.0.0.1:8000/analyze",
                json={"symptoms": symptoms}
            )
            
            if response.status_code == 429:
                print("Rate limited - please wait before retrying")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        print("Request timed out")
        return None
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except json.JSONDecodeError:
        print("Invalid JSON response")
        return None
```

---

## Support

For issues or questions:

1. Check [README.md](../README.md) for overview
2. See [SETUP_GUIDE.md](../SETUP_GUIDE.md) for development
3. Review [DEPLOYMENT.md](../DEPLOYMENT.md) for deployment
4. Check [CONFIGURATION.md](../CONFIGURATION.md) for configuration

---

**Last Updated:** April 2026
**Version:** 1.1.0

