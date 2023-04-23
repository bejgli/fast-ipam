from pydantic import BaseModel

class AddressBase(BaseModel):
    name: str
    description: str | None = None
    subnet_id: int

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    ip_v4: str | None = None
    ip_v6: str | None = None

    class Config:
        orm_mode = True
