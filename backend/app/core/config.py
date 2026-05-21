from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Trainer"
    DEBUG: bool = False
    ENABLE_DOCS: bool = False
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ai_trainer:ai_trainer@localhost:5432/ai_trainer"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "strict"
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # Email verification delivery
    EMAIL_VERIFICATION_REQUIRED: bool = True
    EMAIL_PROVIDER: str = "auto"

    # Brevo transactional email API
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""
    BREVO_SENDER_NAME: str = "AI Trainer"

    # Resend email API
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = ""
    RESEND_FROM_NAME: str = "AI Trainer"

    # SMTP fallback
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "AI Trainer"
    SMTP_STARTTLS: bool = True
    SMTP_TLS_SERVER_HOSTNAME: str = ""
    SMTP_REQUIRED: bool = False

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""
    VK_CLIENT_ID: str = ""
    VK_CLIENT_SECRET: str = ""

    # OpenAI
    AI_PROVIDER: str = "auto"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.4-mini"
    OPENAI_MINI_MODEL: str = "gpt-5.4-mini"
    OPENAI_PROXY_URL: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_API_KEY_2: str = ""
    ANTHROPIC_API_KEYS: str = ""
    ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"
    ANTHROPIC_TIMEOUT_SECONDS: int = 90

    # Rate Limiting
    REDIS_URL: str = "redis://localhost:6379"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        if isinstance(value, str) and value.lower() in {"dev", "development"}:
            return True
        return value

    model_config = {"env_file": ("../.env", ".env"), "case_sensitive": True, "extra": "ignore"}


settings = Settings()
