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
    prefix="/addresses",
    tags=["addresses"]
)


@router.get("/", response_model=list[schemas.Address], status_code=200)
def get_all_addresses(
    response: Response,
    skip: int | None = 0, 
    limit: int | None = 100, 
    db: Session = Depends(get_db)):

    if not (db_addresses := crud.get_addresses(db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_addresses

    
@router.get("/{id}", response_model=schemas.Address)
def get_address_by_id(id: int, db: Session = Depends(get_db)):

    if not (db_address := crud.get_address_by_id(db=db, address_id=id)):
        raise HTTPException(404, detail="Address not found")

    return db_address


@router.post("/", response_model=schemas.Address, status_code=201)
def create_address(
    address: schemas.AddressCreate,
    db: Session = Depends(get_db)):

    if crud.get_address_by_name(db=db, address_name=address.name):
        raise HTTPException(
            status_code=400, 
            detail="Name already used"
        )
    
    if not crud.get_subnet_by_id(db=db, subnet_id=address.subnet_id):
        raise HTTPException(
            status_code=400, 
            detail=f"Subnet {address.subnet_id} doesn't exist"
        )

    return crud.create_address(db=db, address=address)

