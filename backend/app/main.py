"""
FastAPI Application Factory
Creates and configures the FastAPI application.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .core.config import get_settings
from .api import triage, hospitals
from .models.schemas import HealthResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered medical triage system for smart patient prioritization",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware configuration
    # Allow both localhost (development) and production origins
    allowed_origins = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "https://hospital-queue-optimizer.onrender.com",
        "https://hospital-queue-optimizer-xi.vercel.app",
        "https://vercel.app",  # Allow any Vercel deployment
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
        allow_headers=["*"],  # Allow all headers for development
        expose_headers=["*"],
        max_age=600,  # Cache preflight for 10 minutes
    )
    
    # Include routers
    app.include_router(triage.router)
    app.include_router(hospitals.router)
    
    # Legacy endpoints (for backward compatibility)
    @app.post("/analyze")
    async def legacy_analyze(request: triage.TriageRequest):
        """Legacy endpoint - redirects to /api/v1/analyze"""
        return await triage.analyze(request)
    
    @app.post("/nearby-hospitals")
    async def legacy_hospitals(request: hospitals.NearbyHospitalsRequest):
        """Legacy endpoint - redirects to /api/v1/nearby-hospitals"""
        return await hospitals.nearby_hospitals(request)
    
    # Health check
    @app.get("/health", response_model=HealthResponse)
    async def health():
        """Health check endpoint."""
        return HealthResponse(
            status="ok",
            model=settings.GROQ_MODEL,
            version=settings.APP_VERSION
        )
    
    # Serve frontend
    @app.get("/")
    async def root():
        """Serve the frontend application."""
        frontend_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            return FileResponse(frontend_path)
        
        # Fallback to root index.html
        root_index = Path(__file__).parent.parent.parent / "index.html"
        if root_index.exists():
            return FileResponse(root_index)
            
        return {
            "message": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "endpoints": {
                "analyze": "/api/v1/analyze",
                "hospitals": "/api/v1/nearby-hospitals",
                "health": "/health"
            }
        }
    
    return app


# Create the app instance
app = create_app()
