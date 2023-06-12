from fastapi import APIRouter, Depends, HTTPException, Response, status, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from pydantic import EmailStr, SecretStr

from fastipam import crud, schemas, models
from fastipam.dependencies import (
    get_db,
    get_current_active_user,
    get_current_active_superuser,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[schemas.User], status_code=200)
def get_all_users(
    response: Response,
    skip: int | None = None,
    limit: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not (db_users := crud.get_users(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_users


@router.get("/me", response_model=schemas.User, status_code=200)
def get_user_me(
    current_user: models.User = Depends(get_current_active_user),
):
    return current_user


@router.patch("/me", response_model=schemas.User, status_code=200)
def update_user_me(
    username: str = Body(None),
    email: EmailStr = Body(None),
    password: SecretStr = Body(None),
    db: Session = Depends(get_db),
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
        user.password = None # Különben a régi hashelt jelszó lesz az új jelszó..

    return crud.update_user(db=db, user=user, user_id=current_user.id)


@router.get("/{id}", response_model=schemas.User, status_code=200)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not (db_user := crud.get_user_by_id(db=db, user_id=id)):
        raise HTTPException(404, detail="User not found")

    return db_user


@router.post("/", response_model=schemas.User, status_code=201)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if crud.get_user_by_name(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    return crud.create_user(db=db, user=user)


@router.delete("/{id}", status_code=204)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not crud.get_user_by_id(db=db, user_id=id):
        raise HTTPException(404, detail="User not found")

    return crud.delete_user(db=db, user_id=id)


@router.patch("/{id}", response_model=schemas.User, status_code=200)
def update_user(
    id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
):
    if not crud.get_user_by_id(db=db, user_id=id):
        raise HTTPException(404, detail="User not found")

    if user.username and crud.get_user_by_name(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if user.email and crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    return crud.update_user(db=db, user_id=id, user=user)
