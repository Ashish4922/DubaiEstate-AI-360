"""Central settings, read from environment variables (see .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = (BASE_DIR / os.getenv("DATASET_DIR", "../../DataSets")).resolve()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
APP_ENV = os.getenv("APP_ENV", "development")
