from pydantic import BaseModel
from .address import Address

class SubnetBase(BaseModel):
    ip_v4: int
    ip_v6: int | None = None
    mask: str
    name: str
    description: str | None = None

class SubnetCreate(SubnetBase):
    pass

class Subnet(SubnetBase):
    id: int
    addresses: list[Address] = []

    class Config:
        orm_mode = True
