# Legacy Files Documentation

This document explains the legacy file structure and how the project has evolved.

---

## Overview

The AI Hospital Triage System originally had two architectures:

1. **Legacy Modular Structure** (in `/backend/app/` and `/api/` folders)
   - Separated routes, services, and models
   - Used for exploratory development

2. **Current Single-File Structure** (main.py)
   - Simplified, production-ready implementation
   - All logic in one file for easier deployment
   - Currently maintained and deployed

---

## Legacy Files Location

### `/api/` Folder
```
/api/
├── analyze.py      # Legacy symptom analysis endpoint
├── health.py       # Legacy health check
└── hospitals.py    # Legacy hospital search endpoint
```

**Status:** Deprecated - Not used in current deployment

**Why:** These were part of the initial modular design. Functionality has been consolidated into `main.py`.

### `/backend/app/` Folder
```
/backend/app/
├── main.py         # Legacy FastAPI app (not the current main.py)
├── api/            # Legacy route definitions
├── models/         # Legacy Pydantic schemas
├── services/       # Legacy business logic
└── core/           # Legacy configuration
```

**Status:** Deprecated - Not used in current deployment

**Why:** Experimental structure that was replaced by the simplified single-file approach.

---

## Migration History

### Phase 1: Modular Architecture (Initial)
- Separated concerns (routes, services, models)
- Multiple configuration files
- Harder to deploy (multiple entry points)

### Phase 2: Simplified Single-File (Current)
- All logic in `main.py`
- Single entry point
- Easier deployment to serverless platforms
- Better for Vercel/Render

---

## Should You Use Legacy Files?

### No, unless you are:

1. **Learning** - Studying the evolution of the codebase
2. **Refactoring** - Migrating back to modular structure
3. **Archival** - Documenting project history

### For Production: Use `main.py`

All current deployments use the single-file architecture in `main.py`.

---

## File Mappings

### If you need to understand legacy code:

#### Legacy Hospital Search (`/api/hospitals.py`)
**Current location:** `main.py` lines 453-605
- Function: `nearby_hospitals()`
- Logic: Hospital search with smart filtering

#### Legacy Symptom Analysis (`/api/analyze.py`)
**Current location:** `main.py` lines 327-447
- Function: `analyze()`
- Logic: Triage priority classification

#### Legacy Health Check (`/api/health.py`)
**Current location:** `main.py` lines 335-362
- Function: `health()`
- Logic: System status endpoint

---

## Cleanup Recommendations

### Option 1: Keep for Reference (Recommended)
- Keep legacy files as-is
- Document in this file (already done)
- Don't use them in deployments
- Could be useful for code reviews/audits

### Option 2: Remove Legacy Files
```bash
# Remove legacy modular structure
rm -rf /api/
rm -rf /backend/

# Keep only current production code
# - main.py
# - requirements.txt
# - frontend/
# - docs/
# - .env.example
# - etc.
```

### Option 3: Archive Legacy Files
```bash
# Create archive
tar -czf legacy_architecture.tar.gz /api/ /backend/

# Remove from repository
rm -rf /api/
rm -rf /backend/
```

---

## Code Structure Comparison

### Legacy Modular (NOT USED)
```
Request
  ↓
FastAPI App (/backend/app/main.py)
  ↓
Routes (/backend/app/api/*)
  ↓
Services (/backend/app/services/*)
  ↓
Models (/backend/app/models/*)
  ↓
External APIs
```

### Current Single-File (USED)
```
Request
  ↓
FastAPI App (main.py)
  ↓
Endpoint Function
  ↓
Helper Functions
  ↓
External APIs
```

**Advantages of current approach:**
- Simpler to understand (everything in one place)
- Easier to deploy (single file)
- Better for serverless (cold start time)
- Still well-organized with sections

---

## If You Want to Refactor

### To restore modular structure:

1. **Extract routes** from `main.py` into `backend/app/api/`
2. **Extract services** into `backend/app/services/`
3. **Extract models** into `backend/app/models/`
4. **Create new main.py** that imports from these modules

### Benefits:
- Better code organization for large projects
- Easier scaling (multiple developers)
- Better testability (isolated modules)

### Drawbacks:
- More complex deployment
- Harder to understand dependencies
- More files to track

### Would recommend for 2000+ lines of code

---

## Files Not in Legacy Status

These files ARE actively used:

- ✅ `main.py` - Production API
- ✅ `requirements.txt` - Dependencies
- ✅ `index.html` - Frontend
- ✅ `frontend/` folder - Static assets
- ✅ `docs/API.md` - API documentation
- ✅ `.env.example` - Configuration template
- ✅ `.gitignore` - Git rules
- ✅ `README.md` - Project overview

---

## Maintenance Notes

- Legacy code is not tested or maintained
- Legacy code does not have rate limiting
- Legacy code may use outdated dependencies
- Legacy code structure differs from current
- Do NOT deploy from legacy files

---

## References

- See `main.py` for current implementation
- See `DEPLOYMENT.md` for deployment instructions
- See `SETUP_GUIDE.md` for development setup
- See `docs/API.md` for API reference

---

**Last Updated:** April 2026
