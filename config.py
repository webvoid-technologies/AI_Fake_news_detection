import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

APP_NAME = "AI Fake News Detector"
BRAND = "Webvoid Technologies"
SUPPORT_EMAIL = "studentprogram@webvoidtechnologies.com"

REQUEST_TIMEOUT = 20
MIN_CONTENT_LENGTH = 50

SOCIAL_DOMAINS = {
    "twitter.com": "X (Twitter)",
    "x.com": "X (Twitter)",
    "instagram.com": "Instagram",
    "facebook.com": "Facebook",
    "fb.com": "Facebook",
    "linkedin.com": "LinkedIn",
}


def validate_env() -> list[str]:
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    return missing
