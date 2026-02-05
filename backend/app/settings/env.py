from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'
    ENVIRONMENT: str = 'dev'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'  # standard logging level name
    OBSERVABILITY_LOGS_IN_JSON: bool = False  # emit JSON logs when true

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ''
    AWS_SECRET_ACCESS_KEY: str = ''
    AWS_REGION: str = ''
    S3_PHOTOS_BUCKET: str = 'photos'
    S3_THUMBNAILS_BUCKET: str = 'thumbnails'
    S3_TICKETS_BUCKET: str = 'tickets'
    S3_PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour in seconds

    # Lambda
    TICKET_PDF_LAMBDA_NAME: str = 'ticket-pdf-generator'

    # Cognito
    COGNITO_USER_POOL_ID: str = ''
    COGNITO_CLIENT_ID: str = ''

    # Payment
    PAYMENT_WEBHOOK_URL: str = 'http://localhost:8000/payments/webhook'

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache
def get_env_settings() -> Settings:
    return Settings()
