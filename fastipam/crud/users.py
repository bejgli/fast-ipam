from sqlalchemy.orm import Session

from fastipam import models, schemas

from passlib.hash import bcrypt


# Utils


def get_users(db: Session, skip: int | None, limit: int | None):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int):
    return db.get(models.User, user_id)


def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        active=user.active,
        operator=user.operator,
        superuser=user.superuser,
        password=bcrypt.hash(user.password.get_secret_value()),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.get(models.User, user_id)
    db.delete(db_user)
    db.commit()

    return None


def update_user(db: Session, user: schemas.UserUpdate, user_id: int):
    db_user = db.get(models.User, user_id)

    for k, v in user.dict().items():
        if v is not None: # TODO: jobb update módszer
            if k == "password": #TODO: jobb update módszer
                v = bcrypt.hash(v.get_secret_value())
            setattr(db_user, k, v)

    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str):
    if not (db_user := get_user_by_email(db, email=email)):
        return None
    if not bcrypt.verify(password, str(db_user.password)):
        return None
    # TODO: add login date
    return db_user
