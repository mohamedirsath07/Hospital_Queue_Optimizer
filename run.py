"""
AI Hospital Triage System - Entry Point
Run this file to start the application server.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.main import app
from backend.app.core.config import get_settings


def main():
    """Start the AI Triage System server."""
    import uvicorn
    
    settings = get_settings()
    
    print(f"\n{'='*60}")
    print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*60}")
    print(f"  Model:           {settings.GROQ_MODEL}")
    print(f"  Groq API Key:    {'✓ Configured' if settings.GROQ_API_KEY else '✗ Not Set'}")
    print(f"  Google Maps Key: {'✓ Configured' if settings.GOOGLE_MAPS_API_KEY else '✗ Not Set'}")
    print(f"{'='*60}")
    print(f"  Server:          http://127.0.0.1:8000")
    print(f"  API Docs:        http://127.0.0.1:8000/docs")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main()
