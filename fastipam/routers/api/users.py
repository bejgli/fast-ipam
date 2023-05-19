from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from fastipam import crud, schemas
from fastipam.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_name(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered.")

    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    return crud.create_user(db=db, user=user)
