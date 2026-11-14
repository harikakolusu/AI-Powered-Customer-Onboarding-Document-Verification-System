import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend-specific .env from backend/.env
_BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_BACKEND_DIR / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
SAMPLE_DATA_DIR = STORAGE_DIR / "sample_data"
DB_PATH = STORAGE_DIR / "onboarding.db"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

# AI / LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")

# Verification & Quality Thresholds
BLUR_THRESHOLD = float(os.getenv("BLUR_THRESHOLD", "100.0"))  # Laplacian variance threshold
MIN_IMAGE_WIDTH = 600
MIN_IMAGE_HEIGHT = 400
AUTO_APPROVE_MIN_CONFIDENCE = 0.90
LOW_CONFIDENCE_THRESHOLD = 0.75

# Mandatory Document Types
MANDATORY_DOCUMENTS = ["PAN", "AADHAAR"]
OPTIONAL_DOCUMENTS = ["BANK_STATEMENT"]

