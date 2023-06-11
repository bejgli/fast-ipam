from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError, HTTPException

# from fastapi.exception_handlers import request_validation_exception_handler
from pydantic import ValidationError

import pathlib

from fastipam import routers


description = "Compact IPAM created with FastAPI."
version = "0.1.0"


api_app = FastAPI(
    title="IPAM JSON API",
    description=description,
    version=version,
)

api_app.include_router(routers.api.hosts.router)
api_app.include_router(routers.api.subnet.router)
api_app.include_router(routers.api.users.router)
api_app.include_router(routers.api.login.router)


web_app = FastAPI(
    title="IPAM web app",
    description=description,
    version=version,
)

web_app.include_router(routers.web_app.login.router)
web_app.include_router(routers.web_app.subnets.router)
web_app.include_router(routers.web_app.hosts.router)

web_app.mount("/static", StaticFiles(directory="fastipam/static"), name="static")

# TODO: rakd át máshova.
# app.add_exception_hander, app.add_middleware
template_dir = (pathlib.Path(__file__).parent).joinpath("templates")
templates = Jinja2Templates(directory=template_dir)


@web_app.exception_handler(ValidationError)
async def html_form_validation_exception_handler(
    request: Request,
    exc: ValidationError,
    templates: Jinja2Templates = templates,
):
    context = {"request": request, "error": exc.errors()}

    return templates.TemplateResponse(
        "errors/partials/error.html", context=context, status_code=422
    )


@web_app.exception_handler(RequestValidationError)
def html_request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
    templates: Jinja2Templates = templates,
):
    context = {"request": request, "error": exc.errors()}

    return templates.TemplateResponse(
        "errors/partials/error.html", context=context, status_code=422
    )


@web_app.exception_handler(HTTPException)
def html_http_exception_handler(
    request: Request,
    exc: HTTPException,
    templates: Jinja2Templates = templates,
):
    context = {"request": request, "error": exc.detail}

    match exc.status_code:
        case 401:
            return templates.TemplateResponse(
                "login.html", context=context, status_code=exc.status_code
            )
        case 403:
            return templates.TemplateResponse(
                "login.html", context=context, status_code=exc.status_code
            )
        case 400:
            return templates.TemplateResponse(
                "errors/partials/error.html",
                context=context,
                status_code=exc.status_code,
            )
        case _:
            return templates.TemplateResponse(
                "errors/partials/error.html",
                context=context,
                status_code=exc.status_code,
            )


@web_app.middleware("http")
async def add_auth_header(request: Request, call_next):
    if "access_token" not in request.headers and "access_token" in request.cookies:
        access_token = request.cookies["access_token"]

        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
    response = await call_next(request)

    return response


# Full application
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/api", api_app)
app.mount("/", web_app)
