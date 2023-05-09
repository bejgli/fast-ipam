from pydantic import BaseModel

class AddressBase(BaseModel):
    name: str
    description: str | None = None

class AddressCreate(AddressBase):
    subnet_id: int

class HostUpdate(AddressBase):
    name: str | None

class Address(AddressBase):
    id: int
    ip_v4: str | None = None
    ip_v6: str | None = None
    subnet_id: int

    class Config:
        orm_mode = True

# TODO: validation, create host with specified address.
