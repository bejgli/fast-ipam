from pydantic import BaseModel, validator
from ipaddress import ip_address


class HostBase(BaseModel):
    name: str
    description: str | None = None


class HostCreate(HostBase):
    subnet_id: int
    ip: str | None = None

    @validator("ip")
    def check_ip(cls, v):
        if v:
            ip_address(v)
        return v


class HostUpdate(HostBase):
    name: str | None


class Host(HostBase):
    id: int
    ip: str
    subnet_id: int

    class Config:
        orm_mode = True


