import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "MediLoop Healthcare Platform"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/mediloop"
    )
    
    # JWT Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mediloop_enterprise_secure_jwt_secret_key_2026_x98f3a")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # File Upload Security Constraints
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf"}
    ALLOWED_MIME_TYPES: set = {"image/jpeg", "image/png", "application/pdf"}
    
    # Rate Limiting Controls
    RATE_LIMIT_PER_MINUTE_AUTH: int = int(os.getenv("RATE_LIMIT_PER_MINUTE_AUTH", "60"))
    RATE_LIMIT_PER_MINUTE_UPLOAD: int = int(os.getenv("RATE_LIMIT_PER_MINUTE_UPLOAD", "60"))
    RATE_LIMIT_PER_MINUTE_CHAT: int = int(os.getenv("RATE_LIMIT_PER_MINUTE_CHAT", "120"))
    RATE_LIMIT_PER_MINUTE_GENERAL: int = int(os.getenv("RATE_LIMIT_PER_MINUTE_GENERAL", "300"))

settings = Settings()
