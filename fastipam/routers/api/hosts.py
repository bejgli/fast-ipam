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


router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("/", response_model=list[schemas.Host], status_code=200)
def get_all_hosts(
    response: Response,
    skip: int | None = None,
    limit: int | None = None,
    subnet: str | None = None,
    db: Session = Depends(get_db),
):
    if not (
        db_hosts := crud.get_hosts(
            db, skip=skip, limit=limit, subnet_name=subnet
        )
    ):
        response.status_code = status.HTTP_204_NO_CONTENT

    return db_hosts


@router.get("/{id}", response_model=schemas.Host)
def get_host_by_id(id: int, db: Session = Depends(get_db)):
    if not (db_host := crud.get_host_by_id(db=db, host_id=id)):
        raise HTTPException(404, detail="Address not found")

    return db_host


@router.post("/", response_model=schemas.Host, status_code=201)
def create_host(host: schemas.HostCreate, db: Session = Depends(get_db)):
    if crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    if not (subnet := crud.get_subnet_by_id(db=db, subnet_id=host.subnet_id)):
        raise HTTPException(
            status_code=400, detail=f"Subnet {host.subnet_id} doesn't exist"
        )

    if not (db_host := crud.create_host(db=db, host=host, subnet=subnet)):
        raise HTTPException(
            status_code=400, detail=f"Subnet {host.subnet_id} is full"
        )  # TODO Maybe raise in crud, except here Egyébként # Csak akkor None, ha tele van ?

    return db_host


@router.delete("/{id}", status_code=204)
def delete_host(id: int, db: Session = Depends(get_db)):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Host not found")

    return crud.delete_host(db=db, host_id=id)


@router.patch("/{id}", response_model=schemas.Host, status_code=200)
def update_host(id: int, host: schemas.HostUpdate, db: Session = Depends(get_db)):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Address not found")

    # Unique name check
    if host.name and crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    return crud.update_host(db=db, host_id=id, host=host)
