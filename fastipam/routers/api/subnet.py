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


router = APIRouter(
    prefix="/subnets",
    tags=["subnets"]
)


@router.get("/", response_model=list[schemas.Subnet])
def get_all_subnets(
    response: Response,
    skip: int | None = 0, 
    limit: int | None = 100, 
    db: Session = Depends(get_db)):

    if not (db_subnet := crud.get_subnets(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_subnet


@router.get("/{id}", response_model=schemas.Subnet)
def get_subnet_by_id(id: int, db: Session = Depends(get_db)):

    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=id)):
        raise HTTPException(404, detail="Subnet not found")

    return db_subnet


@router.post("/", response_model=schemas.Subnet, status_code=201)
def create_subnet(
    subnet: schemas.SubnetCreate,
    db: Session = Depends(get_db)):

    #TODO

    return crud.create_subnet(db=db, subnet=subnet)