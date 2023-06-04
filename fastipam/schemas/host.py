from pydantic import BaseModel, validator


class HostBase(BaseModel):
    name: str
    description: str | None = None


class HostCreate(HostBase):
    subnet_id: int


class HostUpdate(HostBase):
    name: str | None


class Host(HostBase):
    id: int
    ip: str
    subnet_id: int

    class Config:
        orm_mode = True


# TODO: validation, create host with specified address.
