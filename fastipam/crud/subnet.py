from sqlalchemy.orm import Session

from fastipam import models, schemas


def create_subnet(db: Session, subnet: schemas.SubnetCreate):
    db_subnet = models.Subnet(**subnet.dict())

    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)

    return db_subnet


def get_subnets(db: Session, skip: int | None, limit: int | None):
    return db.query(models.Subnet).offset(skip).limit(limit).all()


def get_subnet_by_id(db: Session, subnet_id: int):
    return db.query(models.Subnet).filter(models.Subnet.id == subnet_id).first()


def get_subnet_by_name(db: Session, subnet_name: str):
    return db.query(models.Subnet).filter(models.Subnet.name == subnet_name).first()