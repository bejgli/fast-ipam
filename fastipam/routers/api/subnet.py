from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from ipaddress import ip_network

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

    # Convert subnet into ipnetwork object for later
    subnet_netw_obj = ip_network(subnet.ip)
    if subnet.supernet:
        if not (db_supernet := crud.get_subnet_by_id(db, subnet.supernet)):
            raise HTTPException(status_code=400, detail="Supernet doesn't exist")

        # Check if supernet is valid (overlaps subnet and versions match)
        try:
            if not (ip_network(db_supernet.ip)).supernet_of(subnet_netw_obj):  # type: ignore
                raise HTTPException(
                    status_code=400,
                    detail="Selected supernet is not supernet of this subnet",
                )
        # TypeError happens when ip versions don't match
        except TypeError:
            raise HTTPException(
                status_code=400,
                detail="Supernet and subnet IP versions don't match",
            )

    # Check for overlapping subnets excluding supernet
    # IP versions already checked, type can be ignored
    db_subnets = crud.get_subnets_by_version(
        db=db, subnet_version=subnet_netw_obj.version
    )

    for db_subnet in db_subnets:
        db_subnet = ip_network(db_subnet.ip)
        if subnet.supernet:
            if subnet_netw_obj.overlaps(db_subnet) and db_subnet != ip_network(db_supernet.ip):  # type: ignore
                raise HTTPException(
                    status_code=400,
                    detail=f"Subnet conflicts with {db_subnet.exploded}",
                )
        else:
            if subnet_netw_obj.overlaps(db_subnet):
                raise HTTPException(
                    status_code=400,
                    detail=f"Subnet conflicts with {db_subnet.exploded}",
                )

    return crud.create_subnet(
        db=db, subnet=subnet, subnet_version=subnet_netw_obj.version
    )


@router.delete("/{id}", status_code=204)
def delete_subnet(id: int, db: Session = Depends(get_db)):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    return crud.delete_subnet(db=db, subnet_id=id)


@router.patch("/{id}", response_model=schemas.Subnet, status_code=200)
def update_subnet(id: int, subnet: schemas.SubnetUpdate, db: Session = Depends(get_db)):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    # Unique name check
    if subnet.name and crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    return crud.update_subnet(db=db, subnet_id=id, subnet=subnet)
