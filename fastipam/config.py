import secrets
from typing import Any, Literal

from pydantic import BaseSettings, EmailStr, SecretStr, validator, Field, PostgresDsn


class Settings(BaseSettings):
    # Security
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Superuser
    SUPERUSER: str = Field(default="admin")
    SUPERUSER_EMAIL: EmailStr = Field(default="admin@example.com")
    SUPERUSER_PASSWORD: SecretStr = Field(default="admin")

    # Database
    SQLALCHEMY_DATABASE_URL: str = Field(default="sqlite:///ipam.db")
    # TODO: db url parsing + validation

    # DB_TYPE: Literal["sqlite", "mysql", "mariadb", "postgres"] = "sqlite"
    # DB_USER: str | None = None
    # DB_PASSWORD: str | None = None
    # DB_SERVER: str | None = None
    # DB_PORT: str | None = None
    # DB_NAME: str = Field(default="ipam.db")
    # SQLALCHEMY_DATABASE_URI: str | None = None

    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     _type = f"{values.get('DB_TYPE')}://"
    #     _user = values.get('DB_USER' or "")
    #     _password = f":{values.get('DB_PASSWORD')}" or ""
    #     _server = f"@{values.get('DB_SERVER')}" or ""
    #     _port = f":{values.get('DB_PORT') or ''}"
    #     _name = f"/{values.get('DB_NAME')}"

    #     print(f"{_type}{_user}{_password}{_server}{_port}{_name}")
    #     return f"{_type}{_user}{_password}{_server}{_port}{_name}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

# TODO: lrucache
