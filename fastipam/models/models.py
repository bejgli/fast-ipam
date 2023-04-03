from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from fastipam.database import Base


class Subnet(Base):
    __tablename__ = "subnet"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(String, unique=True, index=True)
    ip_v6 = Column(String, unique=True, index=True)
    mask = Column(String, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    addresses = relationship("Address", cascade="all, delete-orphan", back_populates="subnet")
    #address_range = relationship("AddressRange", back_populates="subnet")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(Integer, unique=True, index=True)
    ip_v6 = Column(Integer, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    subnet_id = Column(Integer, ForeignKey("subnet.id"))
    subnet = relationship("Subnet", back_populates="addresses")

#class AddressRange(Base):
#    __tablename__ = "address_range"
#
#    id = Column(Integer, primary_key=True, index=True)
#
#    ip_v4 = Column(Integer, unique=True, index=True)
#    ip_v6 = Column(Integer, unique=True, index=True)
#
#    free = Column(Integer)
#
#    subnet_id = Column(Integer, ForeignKey("subnet.id"))
#    subnet = relationship("Subnet", back_populates="addresses")