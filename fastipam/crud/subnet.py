from sqlalchemy import select
from sqlalchemy.orm import Session, load_only
from ipaddress import ip_network, ip_address, IPv4Network, IPv6Network
from fastipam import models, schemas


# def get_subnet_addresses(db: Session):
#    return db.query(models.Subnet).options(load_only(models.Subnet.ip)).all() # type: ignore


def create_subnet(
    db: Session, subnet: schemas.SubnetCreate, subnet_version: int
) -> models.Subnet:
    db_subnet = models.Subnet(**subnet.dict(), version=subnet_version)

    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)

    return db_subnet


def get_subnets(db: Session, skip: int | None, limit: int | None):
    return db.query(models.Subnet).offset(skip).limit(limit).all()


def get_subnets_by_version(db: Session, subnet_version: int) -> list[models.Subnet]:
    return (
        db.query(models.Subnet)
        .filter(models.Subnet.version == subnet_version)
        .options(load_only(models.Subnet.ip))
        .all()
    )


def get_subnet_by_id(db: Session, subnet_id: int):
    return db.query(models.Subnet).filter(models.Subnet.id == subnet_id).first()


def get_subnet_by_name(db: Session, subnet_name: str):
    return db.query(models.Subnet).filter(models.Subnet.name == subnet_name).first()


def delete_subnet(db: Session, subnet_id: int):
    db_subnet = db.get(models.Subnet, subnet_id)
    db.delete(db_subnet)
    db.commit()

    return None


def update_subnet(db: Session, subnet: schemas.SubnetUpdate, subnet_id: int):
    db_subnet = db.get(models.Subnet, subnet_id)

    # Update only if values are not None
    for k, v in subnet.dict().items():
        if v:
            setattr(db_subnet, k, v)

    db.commit()
    db.refresh(db_subnet)

    return db_subnet
