from fastapi import FastAPI

from fastipam.routers import api, ui

title="FastIPAM"
description="Compact IPAM created with FastAPI."
version="0.1.0"


app = FastAPI(
    title=title,
    description=description,
    version=version,
)


app.include_router(api.hosts.router)
app.include_router(api.subnet.router)
app.include_router(api.users.router)
app.include_router(api.login.router)

app.include_router(ui.login.router)


