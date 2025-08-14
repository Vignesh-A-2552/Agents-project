import os

from dotenv import load_dotenv

# Load environment variables from .env file - force reload
load_dotenv(override=True)

class Settings:
    """Application configuration settings."""

    def __init__(self):
        # Reload environment variables to ensure they're fresh
        load_dotenv(override=True)

    # API Configuration
    APP_TITLE = "Code Review API"
    APP_DESCRIPTION = "AI-powered code review service that analyzes syntax, security, performance, and best practices"
    APP_VERSION = "1.0.0"

    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    RELOAD = True
    LOG_LEVEL = "info"

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # OpenAI Configuration - Use properties to get fresh values
    @property
    def OPENAI_API_KEY(self):
        return os.getenv("OPENAI_API_KEY")

    @property
    def MODEL(self):
        return os.getenv("MODEL")

    @property
    def DATABASE_URL(self):
        return os.getenv("DATABASE_URL", "sqlite:///./users.db")

    # Code Review Settings
    MAX_CODE_LENGTH = 50000
    SUPPORTED_LANGUAGES = ["python", "javascript"]
    SUPPORTED_FILE_TYPES = ["py", "js"]

    # CORS Settings
    CORS_ORIGINS = ["*"]  # Configure appropriately for production
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]

    # Performance Analysis Aspects
    PERFORMANCE_ASPECTS = [
        "time complexity",
        "memory usage",
        "query optimization",
        "loop efficiency",
        "resource management"
    ]

    @classmethod
    def validate_settings(cls):
        """Validate required environment variables."""
        instance = cls() if not hasattr(cls, '_instance') else cls._instance
        missing_vars = []

        if not instance.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
        if not instance.MODEL:
            missing_vars.append("MODEL")

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        return True

settings = Settings()
