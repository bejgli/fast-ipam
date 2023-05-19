from pydantic import BaseModel

class HostBase(BaseModel):
    name: str
    description: str | None = None

class HostCreate(HostBase):
    subnet_id: int

class HostUpdate(HostBase):
    name: str | None

class Host(HostBase):
    id: int
    ip_v4: str | None = None
    ip_v6: str | None = None
    subnet_id: int

    class Config:
        orm_mode = True

# TODO: validation, create host with specified address.
