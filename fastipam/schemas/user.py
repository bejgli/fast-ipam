from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr, validator

from email_validator import validate_email, EmailNotValidError


class UserBase(BaseModel):
    username: str
    email: EmailStr
    active: bool | None = True
    operator: bool | None = False
    superuser: bool | None = False

    @validator("email")
    def check_email(cls, v):
        if v:
            return validate_email(v, check_deliverability=False).email


class UserCreate(UserBase):
    password: SecretStr


class UserUpdate(UserBase):
    username: str | None
    email: EmailStr | None
    active: bool | None
    operator: bool | None
    superuser: bool | None
    password: SecretStr | None


class User(UserBase):
    id: int
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True
