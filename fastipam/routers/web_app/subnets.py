from fastapi import APIRouter, Request, Depends, Response, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session

from ipaddress import ip_network

from fastipam import crud, schemas, models, utils
from fastipam.dependencies import (
    get_templates,
    get_db,
    get_current_active_user,
    get_current_active_opuser,
)


router = APIRouter(tags=["subnets"], prefix="/subnets")


@router.get("/", response_class=HTMLResponse)
def get_all_subnets_html(
    request: Request,
    response: Response,
    skip: int | None = 0,
    limit: int | None = 100,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_user),
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
    current_user: models.User = Depends(get_current_active_user),
):
    if not (db_subnet := crud.get_subnet_by_id(db=db, subnet_id=id)):
        raise HTTPException(404, detail="Subnet not found")

    # TODO: change __dict__ to jsonable_encoder!
    subnet = schemas.Subnet(**db_subnet.__dict__)
    # Hosts need to be saved separately, because db_subnet.__dict__ is removing them.
    subnet.hosts = [schemas.Host(**host.__dict__) for host in db_subnet.hosts]

    #TODO: This includes netw and broadcast addr atm..
    free_space = ip_network(db_subnet.ip).num_addresses - len(subnet.hosts)

    context = {
        "request": request,
        "subnet": subnet,
        "free_space": free_space,
    }

    return templates.TemplateResponse("subnets/subnet-detail.html", context=context)


@router.post("/", response_class=HTMLResponse, status_code=201)
def create_subnet_html(
    request: Request,
    name: str = Form(),
    description: str | None = Form(None),
    location: str | None = Form(None),
    threshold: int = Form(0),
    ip: str = Form(),
    supernet: int | None = Form(None),
    reserve: int | None = Form(None, ge=0, le=5),
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):
    subnet = schemas.SubnetCreate(
        name=name,
        description=description,
        location=location,
        threshold=threshold,
        ip=ip,
        supernet=supernet,
    )

    if crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    # Convert subnet into ipnetwork object for later
    subnet_netw_obj = ip_network(subnet.ip)

    if reserve and subnet_netw_obj.num_addresses - reserve < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough address for {reserve} reserved hosts.",
        )

    db_extg_subnets = crud.get_subnets_by_version(
        db=db, subnet_version=subnet_netw_obj.version
    )
    if subnet.supernet:
        if not (db_supernet := crud.get_subnet_by_id(db, subnet.supernet)):
            raise HTTPException(status_code=400, detail="Supernet doesn't exist")

        utils.check_supernet_validity(ip_network(db_supernet.ip), subnet_netw_obj)

        utils.check_subnet_overlap_supernet(
            db_extg_subnets, subnet_netw_obj, db_supernet.ip
        )
    else:
        utils.check_subnet_overlap(db_extg_subnets, subnet_netw_obj)

    db_subnet = crud.create_subnet(
        db=db, subnet=subnet, subnet_version=subnet_netw_obj.version
    )

    if reserve:
        reserved_hosts = utils.create_reserved_host_list(
            db_subnet.id, subnet_netw_obj, reserve
        )
        crud.create_multiple_hosts(db=db, hosts=reserved_hosts)

    # TODO: remove unnecessary info for the post, 
    # only id, name and ip is used
    # hosts could take a long time to create list of
    # context should be used directly
    subnet = schemas.Subnet(
        id=db_subnet.id,
        name=db_subnet.name,
        ip=db_subnet.ip,
        description=db_subnet.description,
        location=db_subnet.location,
        threshold=db_subnet.threshold,
        supernet=db_subnet.supernet,
        version=db_subnet.version,
        hosts=[schemas.Host(**host.__dict__) for host in db_subnet.hosts],
    )

    context = {
        "request": request,
        "subnet": subnet,
    }
    return templates.TemplateResponse(
        "subnets/partials/subnet-table-row.html", context=context
    )


@router.delete("/{id}", response_class=HTMLResponse)
def delete_subnet_html(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    crud.delete_subnet(db=db, subnet_id=id)

    response = RedirectResponse(
        router.url_path_for("get_all_subnets_html"),
        status_code=200,
        headers={"HX-Redirect": router.url_path_for("get_all_subnets_html")}
    )

    return response


@router.get("/{id}/update", response_class=HTMLResponse, status_code=200)
def update_subnet_html_view(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):
    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    context = {
        "request": request,
        "id": id,
    }

    return templates.TemplateResponse(
        "subnets/partials/subnet-update-form.html", context=context
    )


@router.patch("/{id}", response_class=HTMLResponse, status_code=200)
def update_subnet_html(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    name: str | None = Form(None),
    description: str | None = Form(None),
    location: str | None = Form(None),
    threshold: int = Form(0),
    templates: Jinja2Templates = Depends(get_templates),
    current_user: models.User = Depends(get_current_active_opuser),
):

    subnet = schemas.SubnetUpdate(
        name=name,
        description=description,
        location=location,
        threshold=threshold,
    )

    if not crud.get_subnet_by_id(db=db, subnet_id=id):
        raise HTTPException(404, detail="Subnet not found")

    #TODO: can't change to same name
    if subnet.name and crud.get_subnet_by_name(db=db, subnet_name=subnet.name):
        raise HTTPException(status_code=400, detail="Name already used")

    db_subnet = crud.update_subnet(db=db, subnet_id=id, subnet=subnet)

    subnet_updated = schemas.Subnet(**db_subnet.__dict__)

    context = {
        "request": request,
        "subnet": subnet_updated,
    }

    return templates.TemplateResponse(
        "subnets/partials/subnet-detail-list.html", context=context
    )

