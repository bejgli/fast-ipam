from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session

from typing import Annotated
from datetime import timedelta

from fastipam import crud, schemas, models
from fastipam.dependencies import get_templates, get_db, get_current_active_user
from fastipam.security import create_access_token


router = APIRouter(tags=["login"])


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_user),
):
    context = {"request": request, "user": current_user.username}

    return templates.TemplateResponse("index.html", context=context)


@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    context = {"request": request}

    return templates.TemplateResponse("login.html", context=context, status_code=200)


@router.post("/login", response_class=RedirectResponse, status_code=200)
def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    db_user = crud.users.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=45)
    response = RedirectResponse(
        router.url_path_for("index"),
        status_code=303,
    )
    response.set_cookie(
        key="access_token",
        value=create_access_token(db_user.id, expires_delta=access_token_expires),
        httponly=True,
    )

    return response


@router.get("/logout", response_class=RedirectResponse)
def logout(
    response: Response,
    current_user: models.User = Depends(get_current_active_user),
):
    response = RedirectResponse(
        router.url_path_for("login"),
        status_code=303,
    )

    response.delete_cookie("access_token")
    return response
