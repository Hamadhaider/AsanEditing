import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = (BASE_DIR / os.getenv("OUTPUT_DIR", "../outputs")).resolve()
BROWSER_PROFILE = (BASE_DIR / os.getenv("BROWSER_PROFILE", "./gemini-browser-profile")).resolve()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "fr-FR-VivienneMultilingualNeural")
GEMINI_URL = "https://gemini.google.com/app"
