import secrets

from pydantic import BaseSettings, EmailStr, SecretStr, validator, Field


class Settings(BaseSettings):
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SECRET_KEY: str = secrets.token_urlsafe(32)

    SUPERUSER: str = Field(default="admin")
    SUPERUSER_EMAIL: EmailStr = Field(default="admin@example.com")
    SUPERUSER_PASSWORD: SecretStr = Field(default="admin")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

# TODO: lrucache
