from sqlalchemy.orm import Session

from fastipam import models, schemas


def create_subnet(db: Session, subnet: schemas.SubnetCreate):
    db_subnet = models.Subnet(
        name=subnet.name, 
        ip_v4=subnet.ip_v4, 
        ip_v6=subnet.ip_v6, 
        description=subnet.description, 
        mask=subnet.mask,
    )

    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)

    return db_subnet

def get_subnet_by_id(db: Session, subnet_id: int):
    return db.query(models.Subnet).filter(models.Subnet.id == subnet_id).first()