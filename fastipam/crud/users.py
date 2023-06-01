from sqlalchemy.orm import Session

from fastipam import models, schemas

from passlib.hash import bcrypt


# Utils

def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=bcrypt.hash(user.password.get_secret_value()),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
    

def authenticate_user(db: Session, email: str, password: str):
    if not (db_user := get_user_by_email(db, email=email)):
        return None
    if not bcrypt.verify(password, str(db_user.password)):
        return None
    return db_user
