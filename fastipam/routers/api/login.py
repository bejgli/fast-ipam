from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from typing import Annotated
from datetime import timedelta

from fastipam import crud, schemas
from fastipam.dependencies import get_db
from fastipam.security import create_access_token


router = APIRouter(tags=["login"])


@router.post("/login", response_model=schemas.Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    db_user = crud.users.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=45)

    return {
        "access_token": create_access_token(
            db_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
