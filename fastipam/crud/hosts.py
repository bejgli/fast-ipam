from sqlalchemy.orm import Session

from fastipam import models, schemas


def create_host(db: Session, host: schemas.HostCreate):
    db_host = models.Host(**host.dict())

    db.add(db_host)
    db.commit()
    db.refresh(db_host)

    return db_host


def get_hosts(
    db: Session, skip: int | None, limit: int | None, subnet_name: str | None
):
    if subnet_name:
        db_hosts = (
            db.query(models.Host)
            .join(models.Host.subnet)
            .filter(models.Subnet.name == subnet_name)
            .offset(skip)
            .limit(limit)
        )
    else:
        db_hosts = db.query(models.Host).offset(skip).limit(limit)
    return db_hosts.all()


def get_host_by_id(db: Session, host_id: int):
    return db.query(models.Host).filter(models.Host.id == host_id).first()


def get_host_by_name(db: Session, host_name: str):
    return db.query(models.Host).filter(models.Host.name == host_name).first()


def delete_host(db: Session, host_id: int):
    db_host = db.query(models.Host).filter(models.Host.id == host_id)
    db_host.delete()
    db.commit()

    return None


def update_host(db: Session, host: schemas.HostUpdate, host_id: int):
    db_host = db.query(models.Host).filter(models.Host.id == host_id).first()

    # Update only if values are not None
    for k, v in host.dict().items():
        if v:
            setattr(db_host, k, v)

    db.commit()
    db.refresh(db_host)

    return db_host
