from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers.router import router
from routers.dbrouter import dbrouter
from routers.ormrouter import ormrouter

app = FastAPI()

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
