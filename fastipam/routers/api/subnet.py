from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from sqlalchemy.orm import Session
from ipaddress import ip_network, IPv4Address, IPv6Address

from fastipam import crud, schemas
from fastipam.dependencies import get_db


router = APIRouter(prefix="/subnets", tags=["subnets"])


@router.get("/", response_model=list[schemas.Subnet])
def get_all_subnets(
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
):
    if not (db_subnets := crud.get_subnets(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_subnets


@router.get("/{id}", response_model=schemas.Subnet)
def get_subnet_by_id(id: int, db: Session = Depends(get_db)):
    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=id)):
        raise HTTPException(404, detail="Subnet not found")

    return db_subnet


@router.post("/", response_model=schemas.Subnet, status_code=201)
def create_subnet(subnet: schemas.SubnetCreate, db: Session = Depends(get_db)):
    if crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    if not (db_subnet := crud.create_subnet(db=db, subnet=subnet)):
        raise HTTPException(status_code=400, detail="Subnet conflict")

    return db_subnet


@router.delete("/{id}", status_code=204)
def delete_subnet_by_id(id: int, db: Session = Depends(get_db)):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    return crud.delete_subnet_by_id(db=db, subnet_id=id)
