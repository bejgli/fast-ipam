from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from sqlalchemy.orm import Session
from ipaddress import ip_network, IPv4Address, IPv6Address

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
    """Create a new subnet. Default mask is /32.

    Args:
        subnet (schemas.SubnetCreate): _description_
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    if crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(
            status_code=400, 
            detail="Name already used"
        )

    #TODO

    return crud.create_subnet(db=db, subnet=subnet)


#@router.get("/addresses", status_code=201)
#def test_subnet(subnet: schemas.SubnetCreate):
#    if 
#    address_range = ip_network(subnet.ip_v4).hosts()
#    print(address_range)
#
#    return address_range