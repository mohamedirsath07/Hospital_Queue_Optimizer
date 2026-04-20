# Deployment Guide

Complete step-by-step instructions for deploying the AI Hospital Triage System on Render, Vercel, and other platforms.

---

## Table of Contents

1. [API Key Setup](#api-key-setup)
2. [Local Development](#local-development)
3. [Render Deployment](#render-deployment)
4. [Vercel Deployment](#vercel-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## API Key Setup

### Groq API Key

The Groq API provides access to the Llama 3.3 70B model for AI-powered triage analysis.

**Steps to obtain Groq API Key:**

1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account (no credit card required)
3. Click on **"API Keys"** in the left sidebar
4. Click **"Create API Key"**
5. Copy the generated key (starts with `gsk_`)
6. Store it safely - you'll need it during setup

**Key Details:**
- Free tier includes 14,000 requests per minute
- Perfect for testing and small deployments
- Upgrade to a paid plan for higher limits

### Google Maps API Key

The Google Maps API provides real-time hospital location data and details.

**Steps to obtain Google Maps API Key:**

1. Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a new project:
   - Click the project dropdown at the top
   - Click **"NEW PROJECT"**
   - Name it "Hospital-Triage" (or your choice)
   - Click **"CREATE"**
3. Enable required APIs:
   - Go to **"APIs & Services"** → **"Library"**
   - Search for "Places API"
   - Click it and press **"ENABLE"**
   - Search for "Maps JavaScript API"
   - Click it and press **"ENABLE"**
4. Create API credentials:
   - Go to **"APIs & Services"** → **"Credentials"**
   - Click **"+ CREATE CREDENTIALS"** → **"API Key"**
   - Copy the generated key
5. Configure restrictions (recommended):
   - Click on the API key
   - Set **Application restrictions** to HTTP referrers
   - Set **API restrictions** to only "Places API"

**Key Details:**
- Free tier includes $200 monthly credit
- Typical usage for 10,000 searches ≈ $2-5/month
- Set a quota to avoid unexpected charges

---

## Local Development

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- A terminal/command prompt

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mohamedirsath07/Hospital_Queue_Optimizer.git
   cd Hospital_Queue_Optimizer
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   # On Windows: notepad .env
   # On Mac/Linux: nano .env
   ```

5. **Add your API keys to `.env`:**
   ```
   GROQ_API_KEY=gsk_your_groq_key_here
   GOOGLE_MAPS_API_KEY=AIza_your_google_maps_key_here
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

7. **Access the application:**
   - Open browser: http://127.0.0.1:8000
   - API Swagger UI: http://127.0.0.1:8000/docs
   - API ReDoc: http://127.0.0.1:8000/redoc

---

## Render Deployment

Render is a modern cloud platform that makes deployment simple and free for hobby projects.

### Prerequisites

- Render account (sign up at https://render.com)
- GitHub repository with your code

### Step-by-Step Deployment

**1. Prepare your repository:**

Ensure your repository has:
- `requirements.txt` (already included)
- `.env.example` (already included)
- `main.py` (already included)

**2. Create a Render account:**

- Visit https://render.com
- Sign up using GitHub
- Authorize Render to access your repositories

**3. Create a new Web Service:**

- Click **"New"** button on Render dashboard
- Select **"Web Service"**
- Connect your GitHub repository
- Select the Hospital_Queue_Optimizer repository
- Choose a unique service name (e.g., `hospital-triage-api`)
- Select environment: **Python 3**
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 8080`

**4. Set Environment Variables:**

- In the web service settings, go to **"Environment"**
- Add the following environment variables:
  - `GROQ_API_KEY` = your_groq_api_key
  - `GOOGLE_MAPS_API_KEY` = your_google_maps_key

**5. Deploy:**

- Click **"Create Web Service"**
- Render will automatically deploy your application
- Your service URL will be: `https://your-service-name.onrender.com`

**6. Access your deployment:**

- Frontend: `https://your-service-name.onrender.com`
- API Docs: `https://your-service-name.onrender.com/docs`
- Health check: `https://your-service-name.onrender.com/health`

### Cost and Limits

- Free tier: Up to 0.5 GB RAM, auto-spins down after 15 minutes of inactivity
- Paid tier: Starting at $7/month for 1 GB RAM with no auto-spindown
- Recommended: Start free, upgrade when needed

### Keeping Your App Awake

If using the free tier, your app will spin down. To keep it alive:

1. Use an external service like **UptimeRobot** (free):
   - Create an account at https://uptimerobot.com
   - Add HTTP(S) monitor pointing to your health endpoint
   - Set check interval to 5 minutes

---

## Vercel Deployment

Vercel is optimized for static frontends but can also run backends with serverless functions.

### Prerequisites

- Vercel account (sign up at https://vercel.com)
- GitHub repository

### Step-by-Step Deployment

**1. Install Vercel CLI:**

```bash
npm install -g vercel
```

**2. Create vercel.json (already included):**

The `vercel.json` file contains:
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

**3. Deploy using Vercel CLI:**

```bash
vercel
```

Or deploy using GitHub integration:

1. Push your code to GitHub
2. Go to https://vercel.com/new
3. Select your repository
4. Configure project settings (mostly auto-detected)
5. Add environment variables:
   - `GROQ_API_KEY`
   - `GOOGLE_MAPS_API_KEY`
6. Click **"Deploy"**

**4. Access your deployment:**

- Vercel will provide a URL like: `https://your-app.vercel.app`
- API Docs: `https://your-app.vercel.app/docs`

### Important Notes

- Vercel's free tier has **limited execution time per request** (10 seconds)
- The `/nearby-hospitals` endpoint might timeout for complex queries
- Recommended: Use Render for backend, Vercel for frontend only

---

## Environment Configuration

### Required Environment Variables

```bash
# Groq API (required)
GROQ_API_KEY=gsk_your_key_here

# Google Maps API (required)
GOOGLE_MAPS_API_KEY=AIza_your_key_here
```

### Optional Environment Variables

```bash
# Debug mode
DEBUG=false

# Hospital search radius (meters)
HOSPITAL_SEARCH_RADIUS=5000

# Port (default: 8000)
PORT=8000

# Host (default: 127.0.0.1)
HOST=0.0.0.0
```

### Updating Environment Variables

**On Render:**
1. Go to your Web Service
2. Click **"Settings"** tab
3. Find **"Environment"** section
4. Add or update variables
5. Click **"Save"** (automatic redeploy)

**On Vercel:**
1. Go to your project settings
2. Click **"Environment Variables"**
3. Add or update variables
4. Push a new commit to GitHub to trigger redeploy

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **"GROQ_API_KEY not set" Error**

**Problem:** The application starts but shows warnings about missing API key.

**Solution:**
1. Check that your `.env` file exists in the root directory
2. Verify the file contains: `GROQ_API_KEY=your_actual_key`
3. Restart the application
4. Ensure there are no extra spaces or quotes around the key

**For Render/Vercel:**
1. Go to project settings
2. Add environment variable: `GROQ_API_KEY`
3. Trigger a redeploy

#### 2. **"Invalid Coordinates" Error**

**Problem:** Hospital search returns error about invalid coordinates.

**Solution:**
1. Verify latitude is between -90 and 90
2. Verify longitude is between -180 and 180
3. Check that coordinates are in decimal format (not degrees/minutes/seconds)

**Example of valid coordinates:**
- New York: 40.7128, -74.0060
- London: 51.5074, -0.1278
- Tokyo: 35.6762, 139.6503

#### 3. **"Google Places API: Zero Results"**

**Problem:** No hospitals found near the location.

**Solution:**
1. Check your coordinates are correct
2. Try a major city with hospitals
3. Increase search radius in `.env`: `HOSPITAL_SEARCH_RADIUS=10000`
4. Verify your Google Maps API has "Places API" enabled

#### 4. **Timeout Errors**

**Problem:** Requests time out after 10-30 seconds.

**Solution:**
- On Vercel: This is expected due to 10-second limit
  - Use Render instead for backend
  - Or implement caching
- On Render: Check your service has enough RAM
  - Upgrade from free tier if needed
- Check network connectivity
- Try with simpler queries first

#### 5. **Rate Limit Exceeded**

**Problem:** Too many requests, getting 429 errors.

**Solution:**
- Wait a few minutes before retrying
- Check your API quota usage:
  - Groq: https://console.groq.com/keys
  - Google: https://console.cloud.google.com/apis/dashboard
- Implement client-side request throttling
- Consider upgrading API plans

#### 6. **CORS Errors in Browser**

**Problem:** API calls from frontend blocked by CORS policy.

**Solution:**
- CORS should already be configured in main.py
- If using custom domain, verify it's configured correctly
- Clear browser cache and refresh (Ctrl+F5)
- Check browser console for detailed error

### Debugging

**Enable debug logging:**

1. Modify `main.py` line 296:
   ```python
   app = FastAPI(title="AI Triage System", debug=True)
   ```

2. Check application logs:
   - **Local:** Check terminal output
   - **Render:** Go to "Logs" tab on service page
   - **Vercel:** Go to "Deployments" → "Logs"

**Test API endpoints manually:**

```bash
# Health check
curl https://your-app.example.com/health

# Analyze symptoms
curl -X POST https://your-app.example.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "chest pain"}'
```

**Check API quotas:**

- Groq: https://console.groq.com/keys
- Google: https://console.cloud.google.com/quotas

---

## Support

For additional help:

- Check the [README.md](README.md) for feature overview
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for development setup
- Review [CONFIGURATION.md](CONFIGURATION.md) for all config options
- Check [docs/API.md](docs/API.md) for API documentation

---

**Last Updated:** April 2026
