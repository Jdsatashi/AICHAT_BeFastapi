import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent

APP_NAME = os.getenv("APP_NAME", "FastAPI Application")
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8000))
DEBUG = bool(os.getenv("DEBUG", True))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///")

# Password hashing context
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Timezone settings
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "!@#$%^&*()_+")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
JWT_REFRESH_TOKEN_EXPIRE_DAY = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Admin Password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# OpenAI Secret Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

with open(os.path.join(PROJECT_DIR, 'config.json')) as config_file:
    config = json.load(config_file)

ALLOW_ORIGIN = config.get("ALLOW_CORS", ["http://localhost:3000","http://127.0.0.1:3000",])