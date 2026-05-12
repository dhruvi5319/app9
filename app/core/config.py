import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    TEMP_DIR: str = "/tmp/pdfconverter"
    MAX_FILE_SIZE_BYTES: int = 52428800  # 50 MB
    JOB_TIMEOUT_SECONDS: int = 60
    MAX_CONCURRENT_JOBS: int = 5
    TTL_MINUTES: int = 60
    SWEEP_INTERVAL_MINUTES: int = 10
    ALLOWED_ORIGINS: str = "*"
    LOG_LEVEL: str = "INFO"


settings = Settings()
