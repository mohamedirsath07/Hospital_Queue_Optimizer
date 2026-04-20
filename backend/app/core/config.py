"""
Application Configuration
Handles environment variables and system settings.
"""

import os
import logging
from pathlib import Path
from functools import lru_cache


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Load .env file if exists
def load_env():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().strip().split("\n"):
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


load_env()


class Settings:
    """Application settings loaded from environment variables."""

    # Groq AI Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_PLACES_URL: str = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    GOOGLE_PLACE_DETAILS_URL: str = "https://maps.googleapis.com/maps/api/place/details/json"
    HOSPITAL_SEARCH_RADIUS: int = 5000  # 5km radius

    # App Configuration
    APP_NAME: str = "AI Triage System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    def validate(self):
        """Validate required settings and raise errors if critical config missing."""
        warnings = []
        errors = []

        if not self.GROQ_API_KEY:
            errors.append("GROQ_API_KEY environment variable is required but not set. Get it from https://console.groq.com/")

        if not self.GOOGLE_MAPS_API_KEY:
            warnings.append("GOOGLE_MAPS_API_KEY not set. Hospital search will not work. Get it from https://console.cloud.google.com/")

        # Log warnings
        for warning in warnings:
            logger.warning(f"Configuration Warning: {warning}")

        # Raise errors for missing critical config
        if errors:
            error_msg = "Configuration Error(s):\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            # Don't raise in development, just log
            if not self.DEBUG:
                raise RuntimeError(error_msg)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate()
    return settings

