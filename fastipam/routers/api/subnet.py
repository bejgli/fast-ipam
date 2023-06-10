from fastapi import APIRouter, Depends, HTTPException, Response, status, Body
from sqlalchemy.orm import Session
from ipaddress import ip_network

from fastipam import crud, schemas, utils, models
from fastipam.dependencies import (
    get_db,
    get_current_active_user,
    get_current_active_opuser,
)


router = APIRouter(prefix="/subnets", tags=["subnets"])


@router.get("/", response_model=list[schemas.Subnet])
def get_all_subnets(
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_subnets := crud.get_subnets(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_subnets


@router.get("/{id}", response_model=schemas.Subnet)
def get_subnet_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=id)):
        raise HTTPException(404, detail="Subnet not found")

    return db_subnet


@router.post("/", response_model=schemas.Subnet, status_code=201)
def create_subnet(
    subnet: schemas.SubnetCreate,
    reserve: int | None = Body(None, ge=0, le=5),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    # Convert subnet into ipnetwork object for later
    subnet_netw_obj = ip_network(subnet.ip)

    if reserve and subnet_netw_obj.num_addresses - reserve < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough address for {reserve} reserved hosts.",
        )

    db_extg_subnets = crud.get_subnets_by_version(
        db=db, subnet_version=subnet_netw_obj.version
    )
    if subnet.supernet:
        if not (db_supernet := crud.get_subnet_by_id(db, subnet.supernet)):
            raise HTTPException(status_code=400, detail="Supernet doesn't exist")

        utils.check_supernet_validity(ip_network(db_supernet.ip), subnet_netw_obj)

        utils.check_subnet_overlap_supernet(
            db_extg_subnets, subnet_netw_obj, db_supernet.ip
        )
    else:
        utils.check_subnet_overlap(db_extg_subnets, subnet_netw_obj)

    db_subnet = crud.create_subnet(
        db=db, subnet=subnet, subnet_version=subnet_netw_obj.version
    )

    if reserve:
        reserved_hosts = utils.create_reserved_host_list(
            db_subnet.id, subnet_netw_obj, reserve
        )
        crud.create_multiple_hosts(db=db, hosts=reserved_hosts)

    return db_subnet


@router.delete("/{id}", status_code=204)
def delete_subnet(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    return crud.delete_subnet(db=db, subnet_id=id)


@router.patch("/{id}", response_model=schemas.Subnet, status_code=200)
def update_subnet(
    id: int,
    subnet: schemas.SubnetUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    # Unique name check
    if subnet.name and crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    return crud.update_subnet(db=db, subnet_id=id, subnet=subnet)
