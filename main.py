from fastapi import (
    FastAPI,
    Response,
    Request,
    Query,
    HTTPException,
    Cookie,
    Depends,
    status,
)
from pydantic import BaseModel
from hashlib import sha256, sha512
from datetime import timedelta, date
from typing import Optional, List
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.templating import Jinja2Templates
from fastapi_mako import FastAPIMako
from routers.router import router
from routers.dbrouter import dbrouter
from routers.ormrouter import ormrouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

MAX_QUEUE_SIZE = 3

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.include_router(router, prefix="/v1", tags=["api_v1"])
app.include_router(dbrouter, prefix="/db", tags=["sqlite_ver"])
app.include_router(ormrouter, prefix="/orm", tags=["orm_postgres_ver"])
app.include_router(ormrouter, tags=["default"])


templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
def welcome_jinja(request: Request):
    return templates.TemplateResponse(
        "welcome.html.j2",
        {"request": request},
    )