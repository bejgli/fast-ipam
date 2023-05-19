from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from fastipam.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)
    password = Column(String)
    #salt
    email = Column(String, unique=True, index=True)
    
    role = Column(String, default="Read")
    date_created = Column(DateTime, default=datetime.now)
    date_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Section(Base):
    __tablename__ = "section"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    #subnets = relationship(
    #    "Subnet",
    #    cascade="all, delete, delete-orphan",
    #    back_populates="subnet",
    #    passive_deletes=True,
    #)
    
    # subnets should be unique
    # subnets should not overlap -> calculate overlaps

class Subnet(Base):
    __tablename__ = "subnet"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(String, index=True)
    ip_v6 = Column(String, index=True)
    name = Column(String, unique=False, index=True)
    description = Column(String, index=False)
    location = Column(String, index=True)
    threshold = Column(Integer, index=False)

    hosts = relationship(
        "Host",
        cascade="all, delete, delete-orphan",
        back_populates="subnet",
        passive_deletes=True,
    )


class Host(Base):
    __tablename__ = "host"

    id = Column(Integer, primary_key=True, index=True)

    ip_v4 = Column(Integer, index=True)
    ip_v6 = Column(Integer, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, index=False)

    subnet_id = Column(Integer, ForeignKey("subnet.id", ondelete="CASCADE"))
    subnet = relationship("Subnet", back_populates="hosts")
