# Configuration Guide

Complete reference for all environment variables, configuration options, and settings for the AI Hospital Triage System.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Configuration Files](#configuration-files)
3. [Default Values](#default-values)
4. [Examples](#examples)
5. [Advanced Settings](#advanced-settings)

---

## Environment Variables

### Required Variables

These variables **must** be set for the application to function properly.

#### `GROQ_API_KEY`

- **Type:** String
- **Description:** API key for accessing the Groq AI service (Llama 3.3 70B model)
- **Obtain from:** https://console.groq.com/
- **Format:** Starts with `gsk_` followed by alphanumeric characters
- **Example:** `GROQ_API_KEY=gsk_abc123def456...`
- **Required:** Yes
- **Behavior if missing:** Application starts with warning, AI analysis will fail

#### `GOOGLE_MAPS_API_KEY`

- **Type:** String
- **Description:** API key for accessing Google Maps Places API
- **Obtain from:** https://console.cloud.google.com/
- **Format:** Starts with `AIza_` followed by characters
- **Example:** `GOOGLE_MAPS_API_KEY=AIza_abc123def456...`
- **Required:** Yes
- **Behavior if missing:** Hospital search will fail
- **Restrictions:** Should be restricted to Places API only for security

---

### Optional Variables

These variables are optional and have sensible defaults.

#### `DEBUG`

- **Type:** Boolean (true/false)
- **Description:** Enable debug mode for detailed logging
- **Default:** false
- **Example:** `DEBUG=false`
- **Effect:** 
  - When true: Detailed error messages and logs
  - When false: Minimal logging

#### `HOSPITAL_SEARCH_RADIUS`

- **Type:** Integer (meters)
- **Description:** Search radius for nearby hospitals
- **Default:** 5000 (5 kilometers)
- **Range:** 1000-50000 (1-50 km recommended)
- **Example:** `HOSPITAL_SEARCH_RADIUS=10000`
- **Effect:** Larger values return more hospitals but may be slower

#### `PORT`

- **Type:** Integer
- **Description:** Server port number
- **Default:** 8000
- **Range:** 1024-65535
- **Example:** `PORT=8080`
- **Note:** Must be available and not in use by other services

#### `HOST`

- **Type:** String (IP address)
- **Description:** Server host binding
- **Default:** 127.0.0.1 (localhost only)
- **Options:**
  - `127.0.0.1` - Local machine only
  - `0.0.0.0` - All network interfaces (required for cloud deployment)
  - Specific IP - Bind to specific interface
- **Example:** `HOST=0.0.0.0`

#### `WORKERS`

- **Type:** Integer
- **Description:** Number of worker processes (async workers)
- **Default:** 4
- **Range:** 1-16 (recommended)
- **Example:** `WORKERS=8`
- **Effect:** More workers = higher concurrency

---

## Configuration Files

### .env File

**Location:** Root directory (`Hospital_Queue_Optimizer/.env`)

**Purpose:** Store sensitive configuration locally

**Format:**
```
KEY=value
# Comments start with #
ANOTHER_KEY=another_value
```

**Never commit to Git:** Add to `.gitignore` (already done)

**Example .env:**
```bash
# AI Model Configuration
GROQ_API_KEY=gsk_your_actual_key_here

# Maps Configuration
GOOGLE_MAPS_API_KEY=AIza_your_actual_key_here

# Server Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### .env.example File

**Location:** Root directory (`Hospital_Queue_Optimizer/.env.example`)

**Purpose:** Template for setting up local environment

**Usage:**
```bash
cp .env.example .env
# Then edit .env with your actual keys
```

### vercel.json

**Location:** Root directory

**Purpose:** Configuration for Vercel deployment

**Default contents:**
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### requirements.txt

**Location:** Root directory

**Purpose:** Python package dependencies

**Update procedure:**
```bash
# Add new package
pip install package-name
pip freeze > requirements.txt

# Install existing requirements
pip install -r requirements.txt
```

---

## Default Values

| Setting | Default | Type | Required |
|---------|---------|------|----------|
| GROQ_API_KEY | (empty) | string | Yes |
| GOOGLE_MAPS_API_KEY | (empty) | string | Yes |
| DEBUG | false | boolean | No |
| HOSPITAL_SEARCH_RADIUS | 5000 | integer | No |
| PORT | 8000 | integer | No |
| HOST | 127.0.0.1 | string | No |
| WORKERS | 4 | integer | No |

---

## Examples

### Local Development Setup

Create a `.env` file:

```bash
# Core APIs (required)
GROQ_API_KEY=gsk_abc123abc123abc123abc123...
GOOGLE_MAPS_API_KEY=AIza_xyzxyzxyzxyzxyzxyzxyz...

# Development settings
DEBUG=true
HOST=127.0.0.1
PORT=8000
HOSPITAL_SEARCH_RADIUS=5000
```

Run locally:
```bash
python main.py
```

### Production Setup on Render

Set environment variables in Render dashboard:

```
GROQ_API_KEY=gsk_abc123abc123abc123abc123...
GOOGLE_MAPS_API_KEY=AIza_xyzxyzxyzxyzxyzxyzxyz...
DEBUG=false
HOST=0.0.0.0
PORT=8080
WORKERS=8
HOSPITAL_SEARCH_RADIUS=5000
```

Render automatically detects `PORT` environment variable.

### Production Setup on Vercel

Environment variables in project settings:

```
GROQ_API_KEY=gsk_abc123abc123abc123abc123...
GOOGLE_MAPS_API_KEY=AIza_xyzxyzxyzxyzxyzxyzxyz...
DEBUG=false
```

Vercel manages PORT and HOST automatically.

---

## Advanced Settings

### Model Configuration

The application uses **Llama 3.3 70B** model. This is set in `main.py`:

```python
GROQ_MODEL = "llama-3.3-70b-versatile"
```

**To use a different model:**

1. Edit `main.py` line 36
2. Available models at https://console.groq.com/docs/models
3. Options: llama-3.1-70b, mixtral-8x7b, etc.

### API Timeouts

Configurable in `main.py`:

- **Groq API timeout:** 30 seconds (line 354)
- **Google Places timeout:** 10 seconds (line 469)

**To modify:**
```python
# Change timeout values (in seconds)
async with httpx.AsyncClient(timeout=30.0) as client:
```

### Temperature and Tokens

AI model behavior configured in `main.py`:

```python
{
    "model": GROQ_MODEL,
    "temperature": 0.1,      # Lower = more deterministic
    "max_tokens": 500        # Response length limit
}
```

**Recommendations:**
- `temperature`: 0.1 (very focused, good for medical triage)
- `max_tokens`: 500 (enough for detailed responses)

### Rate Limiting

Default rate limits (implement via slowapi):

- **Per IP:** 100 requests/minute
- **Per IP:** 1000 requests/hour

Can be configured when initializing rate limiter.

### Hospital Filtering

Condition keywords in `main.py` (lines 69-95):

```python
CONDITION_KEYWORDS = {
    "CARDIAC": [...],
    "TRAUMA": [...],
    "NEURO": [...],
    "GENERAL": [...]
}
```

**To add custom keywords:**

1. Edit the dictionaries in `main.py`
2. Add new conditions or keywords
3. Restart application

### CORS Configuration

Currently allows all origins (line 298-304):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For production, restrict to:**
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

---

## Environment Variable Loading

The application loads variables in this order:

1. **System environment variables** (highest priority)
2. **.env file** (if exists in root directory)
3. **Default values** (lowest priority)

**To set environment variable:**

```bash
# Windows (cmd)
set GROQ_API_KEY=your_key

# Windows (PowerShell)
$env:GROQ_API_KEY="your_key"

# Linux/Mac
export GROQ_API_KEY=your_key
```

---

## Validation

The application validates:

- ✅ API keys format (non-empty strings)
- ✅ Coordinates (-90 to 90 latitude, -180 to 180 longitude)
- ✅ Port number (1024-65535)
- ✅ JSON request format via Pydantic

**Invalid configuration effects:**

- Missing GROQ_API_KEY: API analysis fails (returns URGENT as fallback)
- Missing GOOGLE_MAPS_API_KEY: Hospital search fails
- Invalid coordinates: Returns error response
- Invalid port: Application fails to start

---

## Performance Tuning

### For High Load

```bash
WORKERS=16                      # More concurrent requests
HOSPITAL_SEARCH_RADIUS=3000    # Faster searches
```

### For Development

```bash
DEBUG=true                      # Detailed logging
HOSPITAL_SEARCH_RADIUS=5000    # More hospitals for testing
```

### For Small Deployments

```bash
WORKERS=2                       # Lower memory usage
HOSPITAL_SEARCH_RADIUS=5000    # Standard search
```

---

## Troubleshooting Configuration

**Problem:** Application starts but endpoints return 500 errors

**Check:**
- Verify `GROQ_API_KEY` is set correctly
- Verify `GOOGLE_MAPS_API_KEY` is set correctly
- Check application logs for specific errors

**Problem:** Hospital search returns 0 results

**Check:**
- Verify coordinates are correct (decimal format)
- Increase `HOSPITAL_SEARCH_RADIUS`
- Confirm Google Maps API is enabled

**Problem:** Rate limiting not working

**Check:**
- Verify slowapi is installed
- Check rate limiter configuration
- Confirm middleware is registered

---

## Security Best Practices

1. **Never commit `.env` file to Git**
   - Already in `.gitignore`

2. **Use strong API keys**
   - Don't reuse keys across projects
   - Rotate keys periodically

3. **Restrict API permissions**
   - Google Maps: Restrict to Places API only
   - Groq: Use project-specific keys

4. **Monitor API usage**
   - Check quotas regularly
   - Set up alerts for unusual activity
   - Implement usage caps

5. **Use HTTPS in production**
   - Render/Vercel automatically use HTTPS
   - Never send API keys over HTTP

---

**Last Updated:** April 2026
