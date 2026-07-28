import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", "")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

# LLM (Google Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.6-flash")
GEMINI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-flash-latest,gemini-3.5-flash,gemini-3.1-flash-lite").split(",")
    if model.strip()
]
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", 800))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.2))

ENABLE_WEB_FALLBACK = os.getenv("ENABLE_WEB_FALLBACK", "1").strip() not in ("0", "false", "False")
WEB_MAX_RESULTS = int(os.getenv("WEB_MAX_RESULTS", 5))
WEB_TIMEOUT_S = int(os.getenv("WEB_TIMEOUT_S", 12))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 25))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 14))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 30))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "1").strip() not in ("0", "false", "False")
