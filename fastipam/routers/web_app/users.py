from fastapi import APIRouter, Request, Depends, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr, SecretStr

from sqlalchemy.orm import Session

from ipaddress import ip_network, ip_address

from fastipam import crud, schemas, models, utils
from fastipam.dependencies import (
    get_templates,
    get_db,
    get_current_active_user,
    get_current_active_opuser,
    get_current_active_superuser,
)


router = APIRouter(tags=["users"], prefix="/users")


@router.get("/", response_class=HTMLResponse)
def get_all_users_html(
    request: Request,
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not (db_users := crud.get_users(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    users = [schemas.User(**db_user.__dict__) for db_user in db_users]

    context = {
        "request": request,
        "users": users,
    }

    return templates.TemplateResponse("users/users.html", context=context)


@router.get("/me", response_class=HTMLResponse, status_code=200)
def get_user_me_html(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    templates: Jinja2Templates = Depends(get_templates),
):
    user = schemas.User(**current_user.__dict__)
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("users/user-detail.html", context=context)


@router.get("/me/update", response_class=HTMLResponse, status_code=200)
def update_user_me_html_view(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    templates: Jinja2Templates = Depends(get_templates),
):
    context = {"request": request, "user": current_user}
    return templates.TemplateResponse(
        "users/partials/user-update-me-form.html", context=context
    )


@router.patch("/me", response_class=HTMLResponse, status_code=200)
def update_user_me_html(
    request: Request,
    username: str = Form(None),
    email: EmailStr = Form(None),
    password: SecretStr = Form(None),
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_user),
):
    if crud.get_user_by_name(db=db, username=username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if crud.get_user_by_email(db=db, email=email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = schemas.UserUpdate(**jsonable_encoder(current_user))

    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.password = password
    else:
        user.password = None  # Különben a régi hashelt jelszó lesz az új jelszó..

    user_updated = crud.update_user(db=db, user=user, user_id=current_user.id)
    context = {
        "request": request,
        "user": user_updated,
    }

    return templates.TemplateResponse(
        "users/partials/user-detail-list.html", context=context
    )


@router.post("/", response_class=HTMLResponse, status_code=201)
def create_user_html(
    request: Request,
    username: str = Form(),
    email: EmailStr = Form(),
    password: SecretStr = Form(),
    active: bool = Form(False),
    operator: bool = Form(False),
    superuser: bool = Form(False),
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_superuser),
):
    user = schemas.UserCreate(
        username=username,
        email=email,
        password=password,
        active=active,
        operator=operator,
        superuser=superuser,
    )
    if crud.get_user_by_name(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    db_user = crud.create_user(db=db, user=user)

    user_new = schemas.User(**jsonable_encoder(db_user))

    context = {
        "request": request,
        "user": user_new,
    }
    return templates.TemplateResponse(
        "users/partials/user-table-row.html", context=context
    )


@router.get("/{id}", response_class=HTMLResponse, status_code=200)
def get_user_by_id_html(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
    templates: Jinja2Templates = Depends(get_templates),
):
    if not (db_user := crud.get_user_by_id(db=db, user_id=id)):
        raise HTTPException(404, detail="User not found")

    user = schemas.User(**jsonable_encoder(db_user))

    context = {"request": request, "user": user}
    return templates.TemplateResponse("users/user-detail.html", context=context)


@router.get("/{id}/update", response_class=HTMLResponse, status_code=200)
def update_user_html_view(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
    templates: Jinja2Templates = Depends(get_templates),
):
    if not (db_user := crud.get_user_by_id(db=db, user_id=id)):
        raise HTTPException(404, detail="User not found")

    user = schemas.User(**jsonable_encoder(db_user))

    context = {"request": request, "user": user}
    return templates.TemplateResponse(
        "users/partials/user-update-table-form.html", context=context
    )


@router.patch("/{id}", response_class=HTMLResponse, status_code=200)
def update_user_html(
    request: Request,
    id: int,
    active: bool = Form(False),
    operator: bool = Form(False),
    superuser: bool = Form(False),
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_superuser),
):
    user = schemas.UserUpdate(
        username=None,
        email=None,
        password=None,
        active=active,
        operator=operator,
        superuser=superuser,
    )

    user_updated = crud.update_user(db=db, user=user, user_id=id)

    context = {
        "request": request,
        "user": user_updated,
    }

    return templates.TemplateResponse(
        "users/partials/user-table-row.html", context=context
    )


@router.delete("/{id}", response_class=HTMLResponse)
def delete_user_html(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not crud.get_user_by_id(db=db, user_id=id):
        raise HTTPException(404, detail="Subnet not found")

    crud.delete_user(db=db, user_id=id)

    return ""