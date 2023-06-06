from fastapi import APIRouter, Request, Depends, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session

from typing import Annotated
from datetime import timedelta
from ipaddress import ip_network, ip_address

from fastipam import crud, schemas, models
from fastipam.dependencies import get_templates, get_db, get_current_active_user
from fastipam.security import create_access_token


router = APIRouter(tags=["subnets"], prefix="/subnets")


@router.get("/", response_class=HTMLResponse)
def get_all_subnets_html(
    request: Request,
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    # current_user: models.User = Depends(get_current_active_user),
):
    if not (db_subnets := crud.get_subnets(db=db, skip=skip, limit=limit)):
        response.status_code = status.HTTP_204_NO_CONTENT

    subnets = [schemas.Subnet(**db_subnet.__dict__) for db_subnet in db_subnets]

    context = {"request": request, "subnets": subnets}

    return templates.TemplateResponse("subnets/subnets.html", context=context)


@router.get("/{id}", response_class=HTMLResponse)
def get_subnet_by_id_html(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    # current_user: models.User = Depends(get_current_active_user),
):
    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=id)):
        raise HTTPException(404, detail="Subnet not found")

    subnet = schemas.Subnet(**db_subnet.__dict__)
    # Hosts need to be saved separately, because db_subnet.__dict__ converting them.
    used_hosts = [schemas.Host(**host.__dict__) for host in db_subnet.hosts]
    valid_hosts = [host for host in ip_network(db_subnet.ip).hosts()]

    free_space = len(valid_hosts) - len(used_hosts)

    context = {
        "request": request,
        "subnet": subnet,
        "free_space": free_space,
        "used_hosts": used_hosts,
    }

    return templates.TemplateResponse("subnets/subnet_detail.html", context=context)


#@router.post("/", response_class=HTMLResponse, status_code=201)
#def create_subnet_html(
#    request: Request,
#    subnet: Annotated[schemas.SubnetCreate, Form()],
#    db: Session = Depends(get_db),
#):
#    if crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
#        raise HTTPException(status_code=400, detail="Name already used")
#
#    # Convert subnet into ipnetwork object for later
#    subnet_netw_obj = ip_network(subnet.ip)
#    if subnet.supernet:
#        if not (db_supernet := crud.get_subnet_by_id(db, subnet.supernet)):
#            raise HTTPException(status_code=400, detail="Supernet doesn't exist")
#
#        # Check if supernet is valid (overlaps subnet and versions match)
#        try:
#            if not (ip_network(db_supernet.ip)).supernet_of(subnet_netw_obj):  # type: ignore
#                raise HTTPException(
#                    status_code=400,
#                    detail="Selected supernet is not supernet of this subnet",
#                )
#        # TypeError happens when ip versions don't match
#        except TypeError:
#            raise HTTPException(
#                status_code=400,
#                detail="Supernet and subnet IP versions don't match",
#            )
#
#    # Check for overlapping subnets excluding supernet
#    # IP versions already checked, type can be ignored
#    db_subnets = crud.get_subnets_by_version(
#        db=db, subnet_version=subnet_netw_obj.version
#    )
#
#    for db_subnet in db_subnets:
#        db_subnet = ip_network(db_subnet.ip)
#        if subnet.supernet:
#            if subnet_netw_obj.overlaps(db_subnet) and db_subnet != ip_network(db_supernet.ip):  # type: ignore
#                raise HTTPException(
#                    status_code=400,
#                    detail=f"Subnet conflicts with {db_subnet.exploded}",
#                )
#        else:
#            if subnet_netw_obj.overlaps(db_subnet):
#                raise HTTPException(
#                    status_code=400,
#                    detail=f"Subnet conflicts with {db_subnet.exploded}",
#                )
#
#    new_db_subnet = crud.create_subnet(
#        db=db, subnet=subnet, subnet_version=subnet_netw_obj.version
#    )
#    return RedirectResponse(
#        router.url_path_for("get_subnet_by_id_html", id=new_db_subnet.id),
#        status_code=303,
#    )
