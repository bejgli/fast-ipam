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
    supernet: int | None = Field(None, ge=1)

    @validator("ip")
    def check_ip(cls, v):
        if v:
            ip_network(v)
        return v
    
   # @root_validator()
   # def check_supernet(cls, values):
   #     if values["supernet"]:
   #         ip_network(values["supernet"]).supernet_of(ip_network(values["ip"])) # type: ignore
   #     return values
   #     # Ez így type error-t dob, ha nem egyezik a két ip verzió (ezért kell a type ignore)
   #     # Ha False, akkor pedig kéne egy raise

class SubnetUpdate(SubnetBase):
    name: str | None
    pass


class Subnet(SubnetBase):
    id: int
    ip: str
    supernet: int | None
    version: int
    hosts: list[Host] = []

    class Config:
        orm_mode = True
