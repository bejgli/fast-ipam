from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from ipaddress import ip_address, ip_network
from sqlalchemy.orm import Session

from fastipam import crud, schemas, models
from fastipam.dependencies import (
    get_db,
    get_current_active_user,
    get_current_active_opuser,
)


router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("/", response_model=list[schemas.Host], status_code=200)
def get_all_hosts(
    response: Response,
    request: Request,
    skip: int | None = None,
    limit: int | None = None,
    subnet: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_hosts := crud.get_hosts(db, skip=skip, limit=limit, subnet_name=subnet)):
        response.status_code = status.HTTP_204_NO_CONTENT

    # print(request.client)
    return db_hosts


@router.get("/{id}", response_model=schemas.Host)
def get_host_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_host := crud.get_host_by_id(db=db, host_id=id)):
        raise HTTPException(404, detail="Address not found")

    return db_host


@router.post("/", response_model=schemas.Host, status_code=201)
def create_host(
    host: schemas.HostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=host.subnet_id)):
        raise HTTPException(
            status_code=400, detail=f"Subnet {host.subnet_id} doesn't exist"
        )

    # Get all used and valid addresses from the selected subnet
    used_hosts = (ip_address(db_host.ip) for db_host in db_subnet.hosts)
    valid_hosts = (host for host in ip_network(db_subnet.ip).hosts())

    # Check if chosen IP is available
    if host.ip:
        if ip_address(host.ip) not in valid_hosts or ip_address(host.ip) in used_hosts:
            raise HTTPException(
                status_code=400,
                detail=f"IP {host.ip} is already taken or not valid in subnet {db_subnet.id}",
            )
    else:
        # Get first free IP address
        if not (
            first_ip := next((addr for addr in valid_hosts if addr not in used_hosts))
        ):
            raise HTTPException(
                status_code=400, detail=f"Subnet {host.subnet_id} is full"
            )
        host.ip = first_ip.exploded

    return crud.create_host(db=db, host=host)


@router.delete("/{id}", status_code=204)
def delete_host(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Host not found")

    return crud.delete_host(db=db, host_id=id)


@router.patch("/{id}", response_model=schemas.Host, status_code=200)
def update_host(
    id: int,
    host: schemas.HostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Address not found")

    # Unique name check
    if host.name and crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    return crud.update_host(db=db, host_id=id, host=host)
