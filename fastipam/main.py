from fastapi import FastAPI

from fastipam.routers.api import addresses, subnet

title="FastIPAM"
description="Compact IPAM created with FastAPI."
version="0.1.0"


app = FastAPI(
    title=title,
    description=description,
    version=version,
)


app.include_router(addresses.router)
app.include_router(subnet.router)


