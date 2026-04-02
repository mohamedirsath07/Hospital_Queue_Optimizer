# 🏥 AI Hospital Triage System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

**An AI-powered medical triage system for smart patient prioritization and hospital recommendations**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-documentation) • [Architecture](#-architecture)

</div>

---

## 🌟 Features

### 🤖 AI-Powered Triage
- **Intelligent Symptom Analysis**: Uses Llama 3.3 70B model via Groq API for accurate urgency classification
- **4-Level Priority System**: Critical, Urgent, Semi-Urgent, and Non-Urgent classifications
- **Safety-First Design**: Never provides diagnoses or medication recommendations

### 🏥 Smart Hospital Finder
- **Real-time Location Detection**: Finds hospitals within 5km radius
- **Condition-Based Matching**: Recommends hospitals based on detected medical condition
- **Smart Filtering**: Excludes diagnostic centers, labs, and pharmacies
- **Direct Integration**: Navigate via Google Maps or call hospitals directly

### 🛡️ Safety Features
- **Input Validation**: Blocks requests for diagnoses or prescriptions
- **Confidence Scoring**: Indicates reliability of each assessment
- **Escalation Triggers**: Warns about symptoms to monitor
- **Professional Disclaimer**: Always reminds users to seek professional care

---

## 📁 Project Structure

```
Hospital_Queue_Optimizer/
├── 📂 backend/
│   └── 📂 app/
│       ├── 📂 api/              # API route handlers
│       │   ├── hospitals.py     # Hospital search endpoints
│       │   └── triage.py        # Symptom analysis endpoints
│       ├── 📂 core/             # Core configuration
│       │   ├── config.py        # Environment settings
│       │   ├── constants.py     # System constants
│       │   └── safety.py        # Input safety filters
│       ├── 📂 models/           # Data models
│       │   └── schemas.py       # Pydantic schemas
│       ├── 📂 services/         # Business logic
│       │   ├── hospital_service.py
│       │   └── triage_service.py
│       └── main.py              # FastAPI application
├── 📂 frontend/
│   ├── index.html               # Main UI
│   └── 📂 static/
│       ├── 📂 css/
│       └── 📂 js/
├── 📂 docs/                     # Documentation
├── 📂 scripts/                  # Utility scripts
│   ├── start.bat                # Windows startup
│   └── start.sh                 # Linux/Mac startup
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Groq API Key ([Get one here](https://console.groq.com))
- Google Maps API Key ([Get one here](https://console.cloud.google.com))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/mohamedirsath07/Hospital_Queue_Optimizer.git
   cd Hospital_Queue_Optimizer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your API keys
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:8000
   ```

---

## 💻 Usage

### Web Interface
1. Open the application in your browser
2. Describe patient symptoms in detail
3. Click "Analyze Symptoms"
4. View triage priority and recommended actions
5. Find nearby hospitals based on your condition

### Quick Test Scenarios
The interface includes pre-built scenarios:
- 🚨 **Critical**: Chest pain emergency
- 🤒 **High Priority**: High fever for 2 days
- 🤕 **Low Priority**: Minor headache

---

## 📚 API Documentation

### Interactive Docs
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Endpoints

#### `POST /api/v1/analyze`
Analyze patient symptoms and return triage priority.

**Request:**
```json
{
  "symptoms": "Severe chest pain radiating to left arm, shortness of breath"
}
```

**Response:**
```json
{
  "priority": 1,
  "priority_label": "CRITICAL",
  "reason": "Chest pain with radiation and breathing difficulty",
  "action": "Immediate cardiac evaluation required",
  "queue": "critical-care",
  "confidence": 0.95,
  "escalation_triggers": ["Loss of consciousness", "Increasing pain"],
  "condition_category": "CARDIAC"
}
```

#### `POST /api/v1/nearby-hospitals`
Find nearby hospitals with condition-based matching.

**Request:**
```json
{
  "lat": 13.0827,
  "lng": 80.2707,
  "symptoms": "chest pain"
}
```

#### `GET /health`
Health check endpoint.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (HTML/JS)                      │
│                    Modern Dark Theme UI                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Triage API  │  │Hospital API │  │   Safety Filter     │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘  │
│         │                │                                   │
│  ┌──────▼──────┐  ┌──────▼──────┐                           │
│  │   Triage    │  │  Hospital   │                           │
│  │  Service    │  │  Service    │                           │
│  └──────┬──────┘  └──────┬──────┘                           │
└─────────┼────────────────┼──────────────────────────────────┘
          │                │
┌─────────▼────────┐ ┌─────▼─────────────┐
│    Groq API      │ │ Google Places API │
│  (Llama 3.3 70B) │ │  (Hospital Data)  │
└──────────────────┘ └───────────────────┘
```

---

## 🔒 Security & Safety

- ✅ No diagnosis or prescription recommendations
- ✅ Input sanitization and validation
- ✅ API key protection via environment variables
- ✅ CORS enabled for secure cross-origin requests
- ✅ Professional medical disclaimer on all responses

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.10+ |
| AI Model | Llama 3.3 70B (via Groq) |
| Frontend | HTML5, CSS3, JavaScript |
| Maps | Google Places API |
| HTTP Client | HTTPX |
| Validation | Pydantic |

---

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for AI model | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Yes |
| `DEBUG` | Enable debug mode | No |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This system is designed as a **decision support tool** for medical triage. It is **NOT** a replacement for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

---

<div align="center">

**Built with ❤️ for better healthcare**

</div>
