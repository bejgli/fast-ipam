from sqlalchemy.orm import Session

from fastipam import crud, schemas
from fastipam.config import settings
from fastipam.database import SessionLocal


def create_initial_superuser(
    db: Session,
):
    if crud.get_user_by_name(db=db, username=settings.SUPERUSER):
        return

    if crud.get_user_by_email(db=db, email=settings.SUPERUSER_EMAIL):
        return 

    user = schemas.UserCreate(
        username=settings.SUPERUSER,
        email=settings.SUPERUSER_EMAIL,
        password=settings.SUPERUSER_PASSWORD,
        active=True,
        operator=True,
        superuser=True,
    )

    return crud.create_user(db=db, user=user)


if __name__ == "__main__":
    db = SessionLocal()
    create_initial_superuser(db=db)
