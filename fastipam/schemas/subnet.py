from pydantic import BaseModel, validator, root_validator, Field
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_network

from .host import Host

class SubnetBase(BaseModel):
    ip: str
    name: str
    description: str | None = None
    location: str | None = None
    threshold: int = Field(0, ge=0, le=100)

    @validator("ip")
    def check_ip(cls, v):
        if v:
            ip_network(v)
        return v


class SubnetCreate(SubnetBase):
    pass


class Subnet(SubnetBase):
    id: int

    hosts: list[Host] = []

    class Config:
        orm_mode = True
