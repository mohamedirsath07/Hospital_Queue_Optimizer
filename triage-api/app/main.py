"""Main FastAPI application."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.config import get_settings
from app.services import llm_service
from app.utils import setup_logging

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger.info("Starting triage API", debug=settings.debug, model=settings.groq_model)
    yield
    # Cleanup
    await llm_service.close()
    logger.info("Triage API shutdown complete")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title="AI Triage System API",
        description="""
## AI-Powered Medical Triage System

This API provides automated triage classification for patient symptoms.

### Safety Features
- **Pre-LLM Safety Filter**: Critical keywords trigger immediate escalation
- **Post-LLM Validation**: Ensures no diagnosis or treatment advice in output
- **Fail-Safe Behavior**: Low confidence scores automatically escalate priority
- **Human-in-the-Loop**: All decisions flagged for staff review

### Important Disclaimer
This system is a **triage aid only**, not a diagnostic tool. All classifications
must be reviewed by qualified healthcare professionals before clinical decisions.
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if settings.debug else None,
            },
        )

    # Include routes
    app.include_router(router, prefix="/api/v1")

    # Root redirect
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "AI Triage API", "docs": "/docs", "health": "/api/v1/health"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
