from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastipam import crud, schemas
from fastipam.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/subnets",
    tags=["subnets"]
)


@router.get("/{id}", response_model=schemas.Subnet)
def get_subnet_by_id(id: int, db: Session = Depends(get_db)):

    return crud.get_subnet_by_id(db=db, subnet_id=id)


@router.post("/", response_model=schemas.Subnet)
def create_subnet(
    subnet: schemas.SubnetCreate,
    db: Session = Depends(get_db)):

    return crud.create_subnet(db=db, subnet=subnet)