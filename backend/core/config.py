from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = Field(default="Task Tracker API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="tasktracker", alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    jwt_secret_key: str = Field(default="eegswgrgdrgbsrdgpppp", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    MAX_TASK_TITLE_LEN: int = 30
    MAX_TASK_DESCRIPTION_LEN: int = 500

    cookie_secure: bool = False

    SMTP_HOST: str = Field(default="localhost", alias="SMTP_HOST")
    SMTP_PORT: int = Field(default=1025, alias="SMTP_PORT")
    SMTP_FROM: str = Field(default="noreply@fatask.local", alias="SMTP_FROM")
    SMTP_USER: str | None = Field(default=None, alias="SMTP_USER")
    SMTP_PASSWORD: str | None = Field(default=None, alias="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=False, alias="SMTP_USE_TLS")

    DATABASE_URL: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    RABBITMQ_URL: str = "amqp://fatask:fatask@localhost:5672//"


settings = Settings()
