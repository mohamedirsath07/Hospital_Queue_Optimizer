# Render Backend Setup & Configuration

## 🚀 Quick Start: Getting Your Backend Running on Render

### Step 1: Set Environment Variables on Render

Your Render backend needs two API keys to function properly:

#### **Option A: With Full Features (Recommended)**

1. **Get Groq API Key:**
   - Go to https://console.groq.com/
   - Sign up or log in
   - Create an API key
   - Copy the key

2. **Get Google Maps API Key:**
   - Go to https://console.cloud.google.com/
   - Create a new project
   - Enable "Places API" and "Maps JavaScript API"
   - Create an API key
   - Copy the key

3. **Add to Render:**
   - Go to your Render dashboard
   - Find your **hospital-queue-optimizer** service
   - Click on **Environment**
   - Add these variables:
     ```
     GROQ_API_KEY=your_groq_key_here
     GOOGLE_MAPS_API_KEY=your_google_maps_key_here
     DEBUG=false
     ```
   - Click **Save**
   - Service will auto-redeploy

#### **Option B: Testing Mode (Without Google Maps)**

If you don't have Google Maps API key yet:

1. Add only Groq API key:
   ```
   GROQ_API_KEY=your_groq_key_here
   DEBUG=false
   ```

2. Hospital search will show message: "Unable to verify facility type - showing nearest available hospitals"

---

## 🔍 Verify Setup

After adding environment variables, test with:

```bash
# Health check (should show api_keys status)
curl https://hospital-queue-optimizer.onrender.com/health

# Test triage (should work with Groq API key)
curl -X POST https://hospital-queue-optimizer.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"Severe chest pain with shortness of breath"}'
```

---

## ✅ Check Status

| Component | Status | What to Check |
|-----------|--------|---------------|
| **CORS** | ✅ Fixed | Frontend can now call backend |
| **Health Endpoint** | ✅ Works | Returns service status & uptime |
| **Triage Analysis** | ⏳ Needs Groq Key | Add GROQ_API_KEY env var |
| **Hospital Search** | ⏳ Needs Google Key | Add GOOGLE_MAPS_API_KEY env var |

---

## 🐛 Troubleshooting

### "Internal Server Error" on /analyze
**Cause:** Missing GROQ_API_KEY  
**Fix:** Add GROQ_API_KEY to Render environment variables

### "Unable to fetch hospital data"
**Cause:** Missing GOOGLE_MAPS_API_KEY  
**Fix:** Add GOOGLE_MAPS_API_KEY to Render environment variables

### "Service not responding"
**Cause:** Render free tier service has spun down  
**Fix:** Visit https://hospital-queue-optimizer.onrender.com/health to wake it up

### CORS Error from Frontend
**Status:** ✅ FIXED  
If you still see CORS errors, clear browser cache and hard refresh (Ctrl+Shift+R)

---

## 🔄 After Setting Environment Variables

1. Variables are saved
2. Service automatically redeploys
3. Wait 1-2 minutes for deployment
4. Test the endpoints again
5. Frontend should now work!

---

## 📊 Current Status

```
Frontend (Vercel):  https://hospital-queue-optimizer-xi.vercel.app
Backend (Render):   https://hospital-queue-optimizer.onrender.com
CORS:               ✅ Enabled
Health Check:       ✅ Working
Triage API:         ⏳ Needs GROQ_API_KEY
Hospital Search:    ⏳ Needs GOOGLE_MAPS_API_KEY
```

---

## 🎯 Next Steps

1. ✅ CORS is fixed - frontend can call backend
2. ⏳ Add GROQ_API_KEY to Render environment
3. ⏳ Add GOOGLE_MAPS_API_KEY to Render environment
4. ✅ Test endpoints
5. ✅ Frontend should work!

**Once you add those API keys, your application will be fully functional!**
