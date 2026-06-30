import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure dirs exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Application Settings
MAX_SEARCH_RESULTS = 5
USER_AGENT = "Mozilla/5.0 (AgenticIA/1.0)"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
