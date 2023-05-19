from fastapi import FastAPI

from fastipam.routers.api import hosts, subnet, users

title="FastIPAM"
description="Compact IPAM created with FastAPI."
version="0.1.0"


app = FastAPI(
    title=title,
    description=description,
    version=version,
)


app.include_router(hosts.router)
app.include_router(subnet.router)
app.include_router(users.router)


