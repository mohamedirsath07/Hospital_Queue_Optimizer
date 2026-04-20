# Setup Guide for Developers

Complete guide for setting up a local development environment and contributing to the AI Hospital Triage System.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Running Tests](#running-tests)
4. [Code Structure](#code-structure)
5. [Contributing Guidelines](#contributing-guidelines)
6. [Development Workflow](#development-workflow)

---

## Prerequisites

Before starting, ensure you have:

### Required

- **Python 3.10 or higher**
  ```bash
  python --version  # Should show 3.10+
  ```

- **Git** (for version control)
  ```bash
  git --version
  ```

- **API Keys** (from development setup)
  - Groq API key (https://console.groq.com/)
  - Google Maps API key (https://console.cloud.google.com/)

### Recommended

- **Git GUI** (GitHub Desktop, Sourcetree)
- **Code Editor** (VS Code recommended)
- **Postman or Insomnia** (for API testing)
- **curl or httpie** (for command-line API testing)

### Optional

- **Docker** (for containerized development)
- **Docker Compose** (for multi-service setup)

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/mohamedirsath07/Hospital_Queue_Optimizer.git
cd Hospital_Queue_Optimizer

# Or using SSH (if configured)
git clone git@github.com:mohamedirsath07/Hospital_Queue_Optimizer.git
cd Hospital_Queue_Optimizer
```

### Step 2: Create Virtual Environment

A virtual environment isolates project dependencies from your system.

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Verify activation:**
```bash
# Your prompt should show (.venv) at the beginning
# Example: (.venv) $ 
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-asyncio httpx
```

**What gets installed:**

| Package | Purpose |
|---------|---------|
| fastapi | Web framework |
| uvicorn | ASGI server |
| httpx | HTTP client |
| pydantic | Data validation |
| python-dotenv | Environment variables |
| pytest | Testing framework |
| pytest-asyncio | Async test support |

### Step 4: Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your keys (use your preferred editor)
# On Windows: notepad .env
# On Mac/Linux: nano .env or vim .env
```

**Add your API keys:**
```bash
GROQ_API_KEY=gsk_your_actual_key_here
GOOGLE_MAPS_API_KEY=AIza_your_actual_key_here
DEBUG=true
```

### Step 5: Verify Installation

```bash
# Check Python
python --version

# Check installed packages
pip list

# Test import
python -c "from fastapi import FastAPI; print('FastAPI OK')"
python -c "from httpx import AsyncClient; print('HTTPX OK')"
```

### Step 6: Run the Application

```bash
# Development mode (with auto-reload)
python main.py
```

**Expected output:**
```
==================================================
AI Triage System Starting...
Model: llama-3.3-70b-versatile
API Key: Set
Google Maps Key: Set
==================================================

INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 7: Access the Application

Open your browser:

- **Frontend:** http://127.0.0.1:8000/
- **API Swagger UI:** http://127.0.0.1:8000/docs
- **API ReDoc:** http://127.0.0.1:8000/redoc
- **Health Check:** http://127.0.0.1:8000/health

---

## Running Tests

### Test Structure

Tests are located in the `tests/` directory (will be created):

```
tests/
├── test_triage.py          # Triage endpoint tests
├── test_hospitals.py       # Hospital search tests
├── test_health.py          # Health endpoint tests
└── conftest.py             # Test configuration
```

### Create Basic Test File

Create `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_analyze_endpoint():
    """Test symptom analysis endpoint."""
    response = client.post(
        "/analyze",
        json={"symptoms": "mild headache"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "priority" in data
    assert "priority_label" in data

def test_nearby_hospitals_invalid_coords():
    """Test nearby hospitals with invalid coordinates."""
    response = client.post(
        "/nearby-hospitals",
        json={"lat": 200, "lng": 400}  # Invalid
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage report
pytest --cov=. tests/

# Watch mode (re-run on file changes)
pytest-watch tests/
```

### Install Testing Tools

```bash
pip install pytest pytest-asyncio pytest-cov pytest-watch
```

### Continuous Testing

For automated testing on file changes:

```bash
# Install watchdog
pip install pytest-watch

# Run tests in watch mode
ptw
```

---

## Code Structure

### Directory Layout

```
Hospital_Queue_Optimizer/
│
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── vercel.json               # Vercel config
│
├── docs/                     # Documentation
│   ├── API.md               # API documentation
│   └── ...
│
├── tests/                    # Test files (create this)
│   ├── test_api.py
│   ├── test_triage.py
│   ├── test_hospitals.py
│   └── conftest.py
│
├── scripts/                  # Utility scripts
│   ├── start.sh
│   ├── start.bat
│   └── ...
│
├── backend/                  # Legacy modular structure
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── models/
│       ├── services/
│       └── core/
│
├── frontend/                 # Frontend files
│   ├── index.html
│   └── static/
│
└── README.md                # Project overview
```

### Main Code Organization (main.py)

**Sections in order:**

1. **Imports** (lines 1-26)
   - Standard library
   - Third-party packages
   - Local modules

2. **Configuration** (lines 28-42)
   - Environment variables
   - API endpoints
   - Model settings

3. **Hospital Filtering** (lines 44-96)
   - Keywords for filtering
   - Condition matching
   - Hospital preferences

4. **Helper Functions** (lines 98-173)
   - Distance calculation
   - Condition classification
   - Hospital validation
   - Score calculation

5. **Data Models** (lines 185-229)
   - Pydantic schemas
   - Request/response types

6. **Safety Filter** (lines 231-262)
   - Blocked patterns
   - Safe response messages

7. **LLM Prompt** (lines 264-290)
   - System prompt
   - Output format

8. **FastAPI App** (lines 292-605)
   - Middleware setup
   - Endpoint definitions
   - Error handling

---

## Contributing Guidelines

### Code Style

**Follow PEP 8:**

```python
# Good
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between coordinates."""
    # Implementation
    return distance

# Bad
def calc_dist(l1,l2,l3,l4):
    # Missing type hints and docstring
    return l1+l2
```

**Type hints are required:**

```python
# Required
def process_symptoms(symptoms: str) -> str:
    """Process and classify symptoms."""
    pass

# Not acceptable
def process_symptoms(symptoms):
    pass
```

**Docstrings for functions:**

```python
def classify_condition(symptoms: str) -> str:
    """
    Classify patient condition based on symptoms.
    
    Args:
        symptoms: Patient symptom description
        
    Returns:
        Condition category (CARDIAC, TRAUMA, NEURO, GENERAL, OTHER)
    """
    pass
```

### Git Workflow

**1. Create a feature branch:**

```bash
git checkout -b feature/your-feature-name
```

**Branch naming convention:**

- `feature/add-rate-limiting`
- `fix/incorrect-distance-calculation`
- `docs/update-api-documentation`
- `refactor/simplify-hospital-scoring`

**2. Make changes:**

```bash
# Edit files
# Test changes
pytest

# Add files to staging
git add .

# Commit with clear message
git commit -m "Add rate limiting middleware with 100 req/min per IP"
```

**3. Commit message format:**

```
[Type] Short description (50 chars or less)

Optional longer explanation if needed.

Fixes #123 (if applicable)
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style (formatting)
- `refactor:` Code refactoring
- `test:` Adding/updating tests
- `chore:` Build, dependencies, etc.

**4. Push to GitHub:**

```bash
git push origin feature/your-feature-name
```

**5. Create Pull Request:**

- Go to GitHub repository
- Click "New Pull Request"
- Select your branch
- Fill in PR template
- Link related issues
- Request reviewers

### Pull Request Checklist

Before submitting:

- [ ] Code follows PEP 8 style guide
- [ ] Type hints added to all functions
- [ ] Docstrings updated
- [ ] Tests added/updated
- [ ] All tests pass (`pytest`)
- [ ] No breaking changes (or documented)
- [ ] README updated if needed
- [ ] No commented-out code
- [ ] No print statements (use logging)

### Common Tasks

**Add a new endpoint:**

```python
@app.post("/new-endpoint")
async def new_endpoint(request: NewRequest) -> NewResponse:
    """
    Endpoint description.
    
    Args:
        request: Request data
        
    Returns:
        Response data
    """
    # Implementation
    return NewResponse(...)
```

**Modify hospital scoring logic:**

Edit `calculate_hospital_score()` function (line 146)

**Update safety filters:**

Edit `BLOCKED_PATTERNS` (line 235) or `SAFE_RESPONSES` (line 245)

**Add new condition category:**

1. Add keywords to `CONDITION_KEYWORDS` (line 69)
2. Add preferences to `CONDITION_HOSPITAL_PREFERENCES` (line 88)
3. Update tests

---

## Development Workflow

### Daily Development

```bash
# Start your day
cd Hospital_Queue_Optimizer
.venv\Scripts\activate  # or source .venv/bin/activate

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/what-you-are-building

# Start development
python main.py

# Make changes in your editor
```

### Testing Before Commit

```bash
# Run all tests
pytest -v

# Run specific test
pytest tests/test_api.py::test_analyze_endpoint

# Run with coverage
pytest --cov=. --cov-report=html

# Type checking (optional)
mypy main.py
```

### Committing Changes

```bash
# Check what changed
git status

# Review changes
git diff

# Add specific files
git add main.py docs/API.md

# Commit with message
git commit -m "feat: add rate limiting middleware"

# Push to remote
git push origin feature/your-feature-name
```

### Before Pushing to Main

```bash
# Ensure all tests pass
pytest

# Verify code style
black . --check  # if using black
flake8 .         # if using flake8

# Update documentation if needed
# Get latest from main
git fetch origin
git rebase origin/main  # or merge if preferred
```

---

## Debugging

### Enable Debug Mode

Edit `.env`:
```bash
DEBUG=true
```

### Using print() for debugging

**Not recommended but quick:**

```python
print(f"DEBUG: hospital_score = {score}")
```

**Better: Use logging:**

```python
import logging

logger = logging.getLogger(__name__)
logger.debug(f"Hospital score: {score}")
logger.info(f"Found {len(hospitals)} hospitals")
logger.warning(f"No hospitals in {radius}m radius")
logger.error(f"API error: {error}")
```

### Debugging API Calls

**Using curl:**

```bash
# GET request
curl http://127.0.0.1:8000/health

# POST request
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "chest pain"}'
```

**Using Postman:**

1. Open Postman
2. Create new request
3. Set method to POST
4. Set URL to `http://127.0.0.1:8000/analyze`
5. Go to Body tab
6. Select JSON format
7. Enter request JSON
8. Click Send

### Using VS Code Debugger

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["main:app", "--reload"],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

Then press F5 to start debugging.

---

## Performance Development Tips

### Profiling

```bash
# Install profiler
pip install py-spy

# Run with profiler
py-spy record -o profile.svg -- python main.py
```

### Async/Await Best Practices

- Use `async`/`await` for I/O operations
- Don't block event loop with CPU-heavy tasks
- Example (Good):
  ```python
  async with httpx.AsyncClient() as client:
      response = await client.get(url)
  ```
- Example (Bad):
  ```python
  import requests
  response = requests.get(url)  # Blocks event loop
  ```

---

## Troubleshooting Development

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** Port 8000 already in use

**Solution:**
```bash
# Use different port
python -m uvicorn main:app --port 8001

# Or kill process using port 8000
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000
```

**Problem:** API keys not being read

**Solution:**
```bash
# Check .env exists
ls -la .env

# Verify keys are set
python -c "import os; print('GROQ:', os.getenv('GROQ_API_KEY'))"

# Restart application
# (CTRL+C then run python main.py again)
```

---

## Getting Help

- Check existing issues: https://github.com/mohamedirsath07/Hospital_Queue_Optimizer/issues
- Read documentation: [README.md](README.md), [docs/API.md](docs/API.md)
- Check configuration: [CONFIGURATION.md](CONFIGURATION.md)
- Review deployment: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Last Updated:** April 2026
