from fastapi import APIRouter, Request, Depends, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session

from ipaddress import ip_network, ip_address

from fastipam import crud, schemas, models, utils
from fastipam.dependencies import (
    get_templates,
    get_db,
    get_current_active_user,
    get_current_active_opuser,
)


router = APIRouter(tags=["hosts"], prefix="/hosts")


@router.get("/", response_class=HTMLResponse)
def get_all_hosts_html(
    request: Request,
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_hosts := crud.get_hosts(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    subnets = crud.get_subnets(db=db, skip=skip, limit=limit)

    hosts = [schemas.Host(**db_host.__dict__) for db_host in db_hosts]

    context = {"request": request, "hosts": hosts, "subnets": subnets}

    return templates.TemplateResponse("hosts/hosts.html", context=context)


@router.get("/{id}", response_class=HTMLResponse)
def get_host_by_id_html(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_host := crud.get_host_by_id(db=db, host_id=id)):
        raise HTTPException(404, detail="Host not found")

    host = schemas.Host(**db_host.__dict__)

    context = {
        "request": request,
        "host": host,
    }

    return templates.TemplateResponse("hosts/host-detail.html", context=context)


@router.post("/", response_class=HTMLResponse, status_code=201)
def create_host_html(
    request: Request,
    name: str = Form(),
    ip: str | None = Form(None),
    subnet_id: int = Form(),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):
    host = schemas.HostCreate(
        name=name,
        ip=ip,
        subnet_id=subnet_id,
        description=description,
    )

    if crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=host.subnet_id)):
        raise HTTPException(
            status_code=400, detail=f"Subnet {host.subnet_id} doesn't exist"
        )

    # Get all used and valid addresses from the selected subnet
    used_hosts = (ip_address(db_host.ip) for db_host in db_subnet.hosts)
    valid_hosts = (host for host in ip_network(db_subnet.ip).hosts())

    # Check if chosen IP is available
    if host.ip:
        if ip_address(host.ip) not in valid_hosts or ip_address(host.ip) in used_hosts:
            raise HTTPException(
                status_code=400,
                detail=f"IP {host.ip} is already taken or not valid in subnet {db_subnet.id}",
            )
    else:
        # Get first free IP address
        if not (
            first_ip := next((addr for addr in valid_hosts if addr not in used_hosts))
        ):
            raise HTTPException(
                status_code=400, detail=f"Subnet {host.subnet_id} is full"
            )
        host.ip = first_ip.exploded

    db_host = crud.create_host(db=db, host=host)

    context = {
        "request": request,
        "host": db_host,
    }

    return templates.TemplateResponse(
        "hosts/partials/host-table-row.html", context=context
    )


@router.delete("/{id}", response_class=HTMLResponse)
def delete_host_html(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Host not found")

    crud.delete_host(db=db, host_id=id)

    response = RedirectResponse(
        router.url_path_for("get_all_hosts_html"),
        status_code=200,
        headers={"HX-Redirect": router.url_path_for("get_all_hosts_html")},
    )

    return response


@router.get("/{id}/update", response_class=HTMLResponse, status_code=200)
def update_host_html_view(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Host not found")

    context = {
        "request": request,
        "id": id,
    }

    return templates.TemplateResponse(
        "hosts/partials/host-update-form.html", context=context
    )


@router.patch("/{id}", response_class=HTMLResponse, status_code=200)
def update_host_html(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    name: str | None = Form(None),
    description: str | None = Form(None),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):
    host = schemas.HostUpdate(
        name=name,
        description=description,
    )

    if not crud.get_host_by_id(db=db, host_id=id):
        raise HTTPException(404, detail="Host not found")

    # TODO: can't change to same name
    if host.name and crud.get_host_by_name(db=db, host_name=host.name):
        raise HTTPException(status_code=400, detail="Name already used")

    db_host = crud.update_host(db=db, host_id=id, host=host)

    host_updated = schemas.Host(**db_host.__dict__)

    context = {
        "request": request,
        "host": host_updated,
    }

    return templates.TemplateResponse(
        "hosts/partials/host-detail-list.html", context=context
    )
