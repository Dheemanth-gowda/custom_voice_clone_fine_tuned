from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic import BaseSettings
import os
from pathlib import Path
import secrets
import torch

class Settings(BaseSettings):
    # Application
    APP_NAME: str
    DEBUG: bool
    ENVIRONMENT: str

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Voice Clone API"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./voice_clone.db"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    AUDIO_DIR: Path = STORAGE_DIR / "audio"
    MODELS_DIR: Path = STORAGE_DIR / "models"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: str
    ERROR_LOG_FILE: str
    ACCESS_LOG_FILE: str

    # Voice Cloning Settings
    VOICE_CLONE_MODEL: str = "tts_models/multilingual/multi-dataset/your_tts"
    VOICE_CLONE_DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    VOICE_CLONE_SAMPLE_RATE: int = 22050
    VOICE_CLONE_HOP_LENGTH: int = 256
    VOICE_CLONE_WIN_LENGTH: int = 1024

    # Storage Quotas
    MODEL_STORAGE_QUOTA: int = 1 * 1024 * 1024 * 1024  # 1GB
    SAMPLE_STORAGE_QUOTA: int = 500 * 1024 * 1024  # 500MB
    GENERATED_STORAGE_QUOTA: int = 2 * 1024 * 1024 * 1024  # 2GB

    # Cleanup Settings
    MODEL_CLEANUP_DAYS: int = 30
    SAMPLE_CLEANUP_DAYS: int = 7
    MAX_MODEL_VERSIONS: int = 5

    # Background Task Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Text Processing Settings
    MAX_TEXT_LENGTH: int = 2000
    BATCH_SIZE: int = 1000

    class Config:
        case_sensitive = True
        env_file = ".env"

    def create_storage_dirs(self):
        """Create necessary storage directories if they don't exist"""
        dirs = [
            self.STORAGE_DIR,
            self.AUDIO_DIR,
            self.AUDIO_DIR / "raw",
            self.AUDIO_DIR / "processed",
            self.AUDIO_DIR / "generated",
            self.MODELS_DIR,
            self.LOGS_DIR,
            self.LOGS_DIR / "error",
            self.LOGS_DIR / "access",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.create_storage_dirs() 