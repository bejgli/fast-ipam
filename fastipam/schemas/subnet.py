from pydantic import BaseModel, validator, root_validator, Field
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_network

from .host import Host

class SubnetBase(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    threshold: int = Field(0, ge=0, le=100)

class SubnetCreate(SubnetBase):
    ip: str

    @validator("ip")
    def check_ip(cls, v):
        if v:
            ip_network(v)
        return v

class SubnetUpdate(SubnetBase):
    name: str | None
    pass

class Subnet(SubnetBase):
    id: int
    ip: str
    hosts: list[Host] = []

    class Config:
        orm_mode = True
