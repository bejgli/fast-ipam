from fastapi import Form
from pydantic import BaseModel, validator, root_validator, Field, ValidationError
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_network

from dataclasses import dataclass

from .host import Host


class SubnetBase(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    threshold: int = Field(0, ge=0, le=100)


class SubnetCreate(SubnetBase):
    ip: str
    supernet: int | None = Field(None, ge=1)
    #reserve: int | None = Field(None, ge=1, le=5)

    @validator("ip")
    def check_ip(cls, v):
        if v:
            ip_network(v)
        return v


class SubnetUpdate(SubnetBase):
    name: str | None


class Subnet(SubnetBase):
    id: int
    ip: str
    supernet: int | None
    version: int
    hosts: list[Host] = []

    class Config:
        orm_mode = True
