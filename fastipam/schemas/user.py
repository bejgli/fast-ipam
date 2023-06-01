from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: SecretStr

class UserUpdate(UserBase):
    pass

class User(UserBase):
    role: str
    date_created: datetime
    date_updated: datetime

    class Config:
        orm_mode = True
