from sqlalchemy.orm import Session, load_only
from ipaddress import ip_network, ip_address, IPv4Network, IPv6Network
from fastipam import models, schemas


# def get_subnet_addresses(db: Session):
#    return db.query(models.Subnet).options(load_only(models.Subnet.ip)).all() # type: ignore


def check_subnet_conflict(new_subnet: IPv4Network | IPv6Network, existing_subnets):
    for subnet in existing_subnets:
        if new_subnet.overlaps(ip_network(subnet.ip)):
            return True  # TODO: Return conflicting IP
    return False


def create_subnet(db: Session, subnet: schemas.SubnetCreate):
    existing_subs = db.query(models.Subnet).options(load_only(models.Subnet.ip)).all() 

    if check_subnet_conflict(ip_network(subnet.ip), existing_subs):
        return None

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


def delete_subnet_by_id(db: Session, subnet_id: int):
    db_subnet = db.get(models.Subnet, subnet_id)
    db.delete(db_subnet)
    db.commit()
    
    return None