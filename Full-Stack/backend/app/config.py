"""Application configuration management for DubaiEstate AI 360 Backend.

Loads environment variables with safe defaults and provides centralized
configuration settings across the application.
"""

import os
from pathlib import Path
from typing import List

# Attempt to load from python-dotenv if available
try:
    from dotenv import load_dotenv
    # Base directory for the backend (Full-Stack/backend)
    BASE_DIR = Path(__file__).resolve().parent.parent
    ENV_PATH = BASE_DIR / ".env"
    if ENV_PATH.is_file():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        load_dotenv()
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    """Application settings and environment configurations."""

    def __init__(self) -> None:
        self.app_name: str = "DubaiEstate AI 360 API"
        self.app_version: str = "0.1.0"
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
        self.backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
        self.api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
        
        # Datasets directory (read-only reference to shared DataSets)
        dataset_rel_path = os.getenv("DATASET_DIR", "../../DataSets")
        self.dataset_dir: Path = (BASE_DIR / dataset_rel_path).resolve()

        # CORS origins
        frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.cors_origins: List[str] = [
            origin.strip() for origin in frontend_origin.split(",") if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() in ("development", "dev")


settings = Settings()
