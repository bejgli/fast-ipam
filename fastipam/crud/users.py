from sqlalchemy.orm import Session

from fastipam import models, schemas

from hashlib import scrypt, sha384


# Utils

def hash_password(plaintext: str):
    salt = "12345"
    hashed_pw = sha384(b"{plaintext}{salt}")

    return hashed_pw.hexdigest()
    


def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
    
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user