from sqlalchemy.orm import Session

from fastipam import models, schemas


def get_addresses(db: Session, skip: int | None, limit: int | None):
    return db.query(models.Address).offset(skip).limit(limit).all()


def get_address_by_id(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def get_address_by_name(db: Session, address_name: str):
    return db.query(models.Address).filter(models.Address.name == address_name).first()


def create_address(db: Session, address: schemas.AddressCreate):
    db_address = models.Address(**address.dict())

    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address