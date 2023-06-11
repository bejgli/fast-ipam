from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

from pydantic import ValidationError
from jose import jwt, JWTError
from sqlalchemy.orm import Session

import pathlib

from fastipam import models, crud, schemas
from fastipam.database import SessionLocal
from fastipam.config import settings


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# TODO: web_app routes use different url
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = crud.users.get_user_by_id(db, user_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return current_user


def get_current_active_opuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not current_user.operator and not current_user.superuser:
        raise HTTPException(
            status_code=403,
            detail="Insufficient privileges. Operator permission required.",
        )

    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="Insufficient privileges. Superuser required."
        )

    return current_user


def get_templates() -> Jinja2Templates:
    template_dir = (pathlib.Path(__file__).parent).joinpath("templates")
    templates = Jinja2Templates(directory=template_dir)

    return templates
