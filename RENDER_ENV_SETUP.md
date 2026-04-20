# 🚨 URGENT: Render Environment Setup Guide

The backend is returning 500 errors because API keys are not being recognized. Follow this EXACT procedure:

## ⚠️ ISSUE
- Health check shows: `"google_maps": "missing"`
- Endpoints return: `Internal Server Error` (500)
- API keys not being read from environment

## ✅ SOLUTION: Set Environment Variables on Render

### **STEP 1: Go to Render Dashboard**
1. Open https://dashboard.render.com
2. Click on your service: **hospital-queue-optimizer**
3. In the left sidebar, click **Environment**

### **STEP 2: Add Variables (EXACT FORMAT)**

Click **Add Environment Variable** and add EACH one separately:

**Variable 1:**
```
Name: GROQ_API_KEY
Value: [Your Groq API Key from console.groq.com]
```

**Variable 2:**
```
Name: GOOGLE_MAPS_API_KEY
Value: [Your Google Maps API Key from console.cloud.google.com]
```

**Variable 3 (Optional but recommended):**
```
Name: DEBUG
Value: false
```

### **STEP 3: CRITICAL - Force Redeploy**

After adding variables:
1. Go to **Deployments** tab (top of page)
2. Click the three dots ⋯ on latest deployment
3. Click **Redeploy**
4. Wait 2-3 minutes for redeployment
5. Status should change from "Building" → "Live"

### **STEP 4: Verify Setup**

Once deployment is complete, test each endpoint:

```bash
# Test 1: Health Check (should show both API keys as "configured")
curl https://hospital-queue-optimizer.onrender.com/health

# Test 2: Triage Analysis
curl -X POST https://hospital-queue-optimizer.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"Severe chest pain with difficulty breathing"}'

# Test 3: Hospital Search  
curl -X POST https://hospital-queue-optimizer.onrender.com/nearby-hospitals \
  -H "Content-Type: application/json" \
  -d '{"lat":13.0827,"lng":80.2707}'
```

## 🔍 Troubleshooting Checklist

- [ ] Variables added exactly as shown above
- [ ] No extra spaces or quotes in values
- [ ] Clicked "Save" after adding each variable
- [ ] Triggered manual redeploy
- [ ] Waited 2-3 minutes for deployment
- [ ] Checked deployment status = "Live"
- [ ] Health endpoint shows both keys as "configured"

## ⏱️ Expected Timeline

1. Add variables: 1 minute
2. Click redeploy: 1 minute  
3. Build & deploy: 2-3 minutes
4. Test endpoints: 1 minute
5. **Total: ~5-7 minutes**

## 🆘 If Still Not Working

### Issue: "Still shows API keys as missing"
- Make sure you clicked **Save** after adding variables
- Make sure you triggered **Redeploy** (not just saving variables)
- Wait full 3 minutes for deployment to complete

### Issue: "Still getting 500 errors"
1. Go to **Logs** tab in Render
2. Look for error messages
3. Share the error with support

### Issue: "Can't find Environment tab"
- Click on the service name
- Look for tabs: **Deploy**, **Events**, **Logs**, **Environment**
- If missing, try refreshing the page

## 📱 Reference Screenshot Locations

On Render Dashboard for your service:
```
Dashboard
├── Your Service (hospital-queue-optimizer)
│   ├── Environment ← CLICK HERE to add variables
│   ├── Deployments ← CLICK HERE to redeploy
│   ├── Logs
│   └── Settings
```

---

**Once variables are added and redeployed, everything will work!** ✅
