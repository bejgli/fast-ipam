from pydantic import BaseModel, validator, root_validator
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_network

from .host import Host

class SubnetBase(BaseModel):
    ip_v4: str | None
    ip_v6: str | None
    name: str
    description: str | None = None
    location: str | None = None
    threshold: int = 0

    @root_validator(pre=True)
    def check_missing(cls, values):
        if not values.get("ip_v4") and not values.get("ip_v6"):
            raise ValueError("Either IPv4 or IPv6 must be provided")
        return values

   # @validator("ip_v4", "ip_v6")
   # def check_ip(cls, v):
   #     if v:
   #         ip_network(v)
   #     return v

    @validator("ip_v4")
    def check_ipv4(cls, v):
        if v:
            IPv4Network(v)
        return v

    @validator("ip_v6")
    def check_ipv6(cls, v):
        if v:
            IPv6Network(v)
        return v

    @validator("threshold")
    def check_threshold(cls, v):
        if not (v >= 0 and v <= 100):
            raise ValueError
        return v


class SubnetCreate(SubnetBase):
    pass


class Subnet(SubnetBase):
    id: int

    hosts: list[Host] = []
    # address_range: list[IPv4Address | IPv6Address] = []

    class Config:
        orm_mode = True
