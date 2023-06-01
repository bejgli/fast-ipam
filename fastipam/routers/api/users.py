from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastipam import crud, schemas, models
from fastipam.dependencies import get_db, get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=201)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if str(current_user.role) != "Write":
        raise HTTPException(status_code=400, detail="Insufficient permissions.")

    if crud.get_user_by_name(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    return crud.create_user(db=db, user=user)
