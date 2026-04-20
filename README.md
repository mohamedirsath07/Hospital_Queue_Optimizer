# 🏥 AI Hospital Triage System

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

**An AI-powered medical triage system for smart patient prioritization and hospital recommendations**

[Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation) • [Deployment](#deployment) • [Contributing](#contributing)

</div>

---

## 📋 Quick Start

### Prerequisites

- Python 3.10+
- Groq API key (free at https://console.groq.com/)
- Google Maps API key (free at https://console.cloud.google.com/)

### Setup (2 minutes)

```bash
# Clone and setup
git clone https://github.com/mohamedirsath07/Hospital_Queue_Optimizer.git
cd Hospital_Queue_Optimizer
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install and configure
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys

# Run
python main.py
```

Then open: http://127.0.0.1:8000

---

## ✨ Features

### 🤖 AI-Powered Triage
- **Intelligent Symptom Analysis**: Llama 3.3 70B model via Groq API
- **4-Level Priority System**: Critical → Urgent → Semi-Urgent → Non-Urgent
- **Safety-First**: Never diagnoses or prescribes medications
- **Confidence Scoring**: Know the reliability of each assessment

### 🏥 Smart Hospital Finder
- **Real-time Location Detection**: Finds hospitals within 5km
- **Condition-Based Matching**: Recommends hospitals for your condition
- **Smart Filtering**: Excludes diagnostic centers, labs, pharmacies
- **Direct Integration**: Call hospitals or navigate via Google Maps

### 🛡️ Safety Features
- **Input Validation**: Blocks inappropriate requests
- **Escalation Triggers**: Warns about symptoms to monitor
- **Professional Disclaimer**: Always reminds users to seek professional care
- **Rate Limiting**: 100 requests/minute per IP for fair access

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [**DEPLOYMENT.md**](DEPLOYMENT.md) | Deploy to Render, Vercel, or cloud platforms |
| [**SETUP_GUIDE.md**](SETUP_GUIDE.md) | Local development setup & testing |
| [**CONFIGURATION.md**](CONFIGURATION.md) | All environment variables & settings |
| [**docs/API.md**](docs/API.md) | Complete API reference with examples |

---

## 🚀 Deployment

### Quick Deployment

**Render (Recommended):**
1. Push to GitHub
2. Go to https://render.com
3. Create Web Service from repository
4. Set environment variables (GROQ_API_KEY, GOOGLE_MAPS_API_KEY)
5. Deploy!

**Vercel:**
1. Install Vercel CLI: `npm install -g vercel`
2. Run: `vercel`
3. Set environment variables in project settings

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Frontend                          │
│                  (HTML/CSS/JavaScript)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Triage API   │  │Hospital API  │  │ Rate Limiting   │   │
│  │ (/analyze)   │  │(/hospitals)  │  │ (100 req/min)   │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────┘   │
│         │                 │                                  │
│  ┌──────▼──────┐  ┌──────▼──────┐                          │
│  │   Groq API  │  │   Google    │                          │
│  │(Llama 3.3)  │  │ Places API  │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 API Endpoints

### Analyze Symptoms

```bash
POST /analyze
{
  "symptoms": "chest pain and shortness of breath"
}
```

Returns: Priority level, reason, recommended action, escalation triggers

### Find Nearby Hospitals

```bash
POST /nearby-hospitals
{
  "lat": 13.0827,
  "lng": 80.2707,
  "symptoms": "chest pain"
}
```

Returns: Top 5 hospitals with distance, phone, match score

### Health Check

```bash
GET /health
```

Returns: System status, version, uptime, API configuration

---

## 💻 Interactive API Docs

Access these after running the application:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 🔧 Configuration

### Required Environment Variables

```bash
GROQ_API_KEY=gsk_your_key_here
GOOGLE_MAPS_API_KEY=AIza_your_key_here
```

### Optional Variables

```bash
DEBUG=false                          # Debug mode
HOSPITAL_SEARCH_RADIUS=5000         # Search radius in meters
PORT=8000                           # Server port
HOST=127.0.0.1                      # Server host
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete reference.

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. tests/
```

### Manual Testing

1. Open http://127.0.0.1:8000
2. Use built-in test scenarios
3. Check API docs at `/docs`

---

## 📁 Project Structure

```
Hospital_Queue_Optimizer/
├── main.py                  # FastAPI application
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── vercel.json             # Vercel config
│
├── docs/
│   └── API.md             # API documentation
├── frontend/
│   ├── index.html         # Web UI
│   └── static/            # Assets
│
├── DEPLOYMENT.md          # Deployment guide
├── SETUP_GUIDE.md         # Development setup
├── CONFIGURATION.md       # Config reference
└── README.md              # This file
```

---

## 🔒 Security

- ✅ No diagnosis or prescription recommendations
- ✅ Input validation and sanitization
- ✅ API keys protected via environment variables
- ✅ CORS enabled for secure cross-origin requests
- ✅ Rate limiting (100 requests/minute per IP)
- ✅ Professional medical disclaimer on all responses

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI, Python 3.10+ |
| **AI Model** | Llama 3.3 70B (via Groq) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Maps** | Google Places API |
| **HTTP Client** | HTTPX (async) |
| **Validation** | Pydantic |
| **Rate Limiting** | SlowAPI |
| **Deployment** | Render, Vercel |

---

## 🤝 Contributing

Contributions are welcome! See [SETUP_GUIDE.md](SETUP_GUIDE.md) for development setup.

### Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Standards

- Follow PEP 8
- Add type hints to all functions
- Include docstrings
- Write tests for new features
- Update documentation

---

## 📈 API Usage Examples

### Python

```python
import httpx
import asyncio

async def triage(symptoms):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/analyze",
            json={"symptoms": symptoms}
        )
        return response.json()

# Run
result = asyncio.run(triage("chest pain"))
print(f"Priority: {result['priority_label']}")
```

### JavaScript

```javascript
async function triage(symptoms) {
    const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({symptoms})
    });
    return await response.json();
}

triage('chest pain').then(result => {
    console.log(`Priority: ${result.priority_label}`);
});
```

### cURL

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"symptoms":"chest pain"}'
```

---

## ⚠️ Medical Disclaimer

This system is designed as a **decision support tool** for medical triage. It is **NOT**:

- A replacement for professional medical advice
- A diagnostic tool
- A prescribing system
- Licensed for clinical use

Always consult qualified healthcare professionals for medical decisions.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

Having issues? Check the docs:

- **Deployment Issues?** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Setup Help?** See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Configuration?** See [CONFIGURATION.md](CONFIGURATION.md)
- **API Questions?** See [docs/API.md](docs/API.md)

---

## 🎯 Roadmap

- [ ] User authentication & session management
- [ ] Patient history tracking
- [ ] Integration with EHR systems
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] WebSocket real-time updates

---

<div align="center">

**Built with ❤️ for better healthcare**

*Version 1.1.0 • Last Updated April 2026*

</div>
