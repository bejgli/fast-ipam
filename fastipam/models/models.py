from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from fastipam.database import Base


class Subnet(Base):
    __tablename__ = "subnet"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(Integer, unique=True, index=True)
    ip_v6 = Column(Integer, unique=True, index=True)
    mask = Column(String, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    addresses = relationship("Address", back_populates="subnet")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(Integer, unique=True, index=True)
    ip_v6 = Column(Integer, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    subnet_id = Column(Integer, ForeignKey("subnet.id"))
    subnet = relationship("Subnet", back_populates="addresses")