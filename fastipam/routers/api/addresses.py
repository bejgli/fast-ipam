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
    prefix="/addresses",
    tags=["addresses"]
)


@router.get("/", response_model=list[schemas.Address])
def get_all_addresses(
    skip: int | None = 0, 
    limit: int | None = 100, 
    db: Session = Depends(get_db)):

    return crud.get_addresses(db, skip=skip, limit=limit)

    
@router.get("/{id}", response_model=schemas.Address)
def get_address_by_id(id: int, db: Session = Depends(get_db)):

    return crud.get_address_by_id(db, address_id=id)


@router.post("/", response_model=schemas.Address)
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

