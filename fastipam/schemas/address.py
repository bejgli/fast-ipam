from pydantic import BaseModel

class AddressBase(BaseModel):
    ip_v4: int
    ip_v6: int | None = None
    name: str
    description: str | None = None
    subnet_id: int

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int

    class Config:
        orm_mode = True
