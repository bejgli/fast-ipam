from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from fastipam.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True)
    operator: Mapped[bool] = mapped_column(Boolean, default=False)
    superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    date_created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    date_updated: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


class Section(Base):
    __tablename__ = "section"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, index=False)

    # subnets = relationship(
    #    "Subnet",
    #    cascade="all, delete, delete-orphan",
    #    back_populates="subnet",
    #    passive_deletes=True,
    # )

    # subnets should be unique
    # subnets should not overlap -> calculate overlaps


class Subnet(Base):
    __tablename__ = "subnet"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    ip: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, unique=False, index=True)
    description: Mapped[str | None]
    location: Mapped[str | None] 
    threshold: Mapped[int] = mapped_column(Integer)

    hosts: Mapped[list["Host"]] = relationship(
        back_populates="subnet",
        cascade="all, delete-orphan",
    )


class Host(Base):
    __tablename__ = "host"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    ip: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] 

    subnet_id: Mapped[int] = mapped_column(ForeignKey("subnet.id"))
    subnet: Mapped["Subnet"] = relationship(back_populates="hosts")
