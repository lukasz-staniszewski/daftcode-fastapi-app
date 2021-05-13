from fastapi import (
    APIRouter,
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
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


router = APIRouter()
MAX_QUEUE_SIZE = 3

router.counter = 0
router.__name__ = "First router"
router.fake_datebase = {}
start = date.today()


objects = {
    1: {"field_a": "a", "field_b": "b"},
    2: {"field_a": "a", "field_b": "b"},
    3: {"field_a": "a", "field_b": "b"},
    # .... #
}

router.secret_key = "very constatn and random secret, best 64+ characters"
router.access_tokens = []

security = HTTPBasic()


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


class RegisteredPerson(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@router.get("/hello/{name}", response_model=HelloResp)
async def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")


@router.get("/")
def root():
    return {"message": "Hello world!"}


@router.get("/counter")
def counter():
    router.counter += 1
    return router.counter


@router.api_route("/method", methods=["GET", "POST", "DELETE", "OPTIONS", "PUT"])
def method(response: Response, request: Request):
    if str(request.method) == "POST":
        response.status_code = 201
    else:
        response.status_code = 200
    return {"method": str(request.method)}


@router.get("/auth/")
async def read_items_auth(
    response: Response,
    password: Optional[str] = None,
    password_hash: Optional[str] = None,
):
    if (
        password == ""
        or password_hash == ""
        or password is None
        or password_hash is None
    ):
        response.status_code = 401
        return
    hashed_password = sha512(password.encode())
    if hashed_password.hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@router.post("/register/", response_model=RegisteredPerson)
async def register(person: Person, response: Response, request: Request):
    response.status_code = 201
    n_of_letters = 0
    for letter in person.name + person.surname:
        if letter.isalpha():
            n_of_letters += 1
    router.counter += 1
    date_then = start + timedelta(days=n_of_letters)
    router.fake_datebase[router.counter] = RegisteredPerson(
        id=router.counter,
        name=person.name,
        surname=person.surname,
        register_date=str(start),
        vaccination_date=str(date_then),
    )
    return RegisteredPerson(
        id=router.counter,
        name=person.name,
        surname=person.surname,
        register_date=str(start),
        vaccination_date=str(date_then),
    )


@router.get("/patient/{patient_id}", response_model=RegisteredPerson)
async def getpatient(patient_id: int, response: Response):
    if patient_id < 1:
        response.status_code = 400
    elif patient_id > router.counter:
        response.status_code = 404
    else:
        response.status_code = 200
        return router.fake_datebase[patient_id]


@router.get("/request_query_string_discovery/")
def get_params(u: str = Query("default"), q: List[str] = Query(None)):
    query_items = {"q": q, "u": u}
    return query_items


@router.get("/static", response_class=HTMLResponse)
def index_static():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """


@router.get("/simple_path_tmpl/{sample_variable}/{sample_2}")
def simple_path_tmpl(sample_variable: str, sample_2: str):
    print(f"{sample_variable=}")
    print(type(sample_variable))
    return {"sample_variable": sample_variable, "sample_2": sample_2}


@router.get("/files/{file_path:path}/terminator/{x1}")
def read_file(file_path: str, x1: str):
    return {"file_path": file_path, "x1": x1}


@router.get("/simple_path_tmpl/{sample_variable}")
def simple_path_tmpl1(sample_variable: str):
    print(f"{sample_variable=}")
    print(type(sample_variable))
    return {"sample_variable": sample_variable}


@router.get("/simple_path_tmpl/{obj_id}/{field}")
def simple_path_tmpl2(obj_id: int, field: str):
    print(f"{obj_id=}")
    print(f"{field=}")
    return {"field": objects.get(obj_id, {}).get(field)}


@router.get("/items/")
def read_items(*, ads_id: str = Cookie(None)):
    return {"ads_id": ads_id}


@router.post("/cookie-and-object/")
def create_cookie(response: Response):
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return {"message": "Come to the dark side, we have cookies"}


@router.post("/login/")
def login(user: str, password: str, response: Response):
    session_token = sha256(f"{user}{password}{router.secret_key}".encode()).hexdigest()
    router.access_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return {"message": "Welcome"}


@router.get("/data/")
def secured_data(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in router.access_tokens:
        raise HTTPException(status_code=403, detail="Unauthorised")
    else:
        return {"message": "Secure content!!!"}


@router.get("/hello", response_class=HTMLResponse)
def hello():
    return f"<h1>Hello! Today date is {start}</h1>"


correct_login = "4dm1n"
correct_passwd = "NotSoSecurePa$$"
router.access_token_session = []
router.access_token_token = []


def check_usrnm_passwd(credentials):
    correct_usrnm = secrets.compare_digest(credentials.username, correct_login)
    correct_password = secrets.compare_digest(credentials.password, correct_passwd)
    if not (correct_usrnm and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised - incorrect login or password!",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.post("/login_session")
def login_session(
    response: Response, credentials: HTTPBasicCredentials = Depends(security)
):
    check_usrnm_passwd(credentials)
    response.status_code = 201
    router.counter += 1
    session_token = sha512(
        f"something_completely_random{router.counter}".encode()
    ).hexdigest()
    add_session_token(session_token, router.access_token_session)
    response.set_cookie(key="session_token", value=session_token)


@router.post("/login_token", response_class=JSONResponse)
def login_token(
    response: Response, credentials: HTTPBasicCredentials = Depends(security)
):
    check_usrnm_passwd(credentials)
    response.status_code = 201
    router.counter += 1
    token_value = sha512(
        f"something_more_completely_random{router.counter}".encode()
    ).hexdigest()
    add_session_token(token_value, router.access_token_token)
    return {"token": token_value}


def check_token(token: str, with_what: str):
    if token is None or token not in with_what:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised - wrong session token",
            headers={"WWW-Authenticate": "Basic"},
        )


def add_session_token(session_token: str, where):
    if len(where) == MAX_QUEUE_SIZE:
        del where[0]
    where.append(session_token)


def remove_session_token(session_token: str, where):
    where.remove(session_token)


@router.get("/welcome_session")
def welcome_session(
    response: Response,
    token: str = Query(None),
    format: str = Query(None),
    session_token: str = Cookie(None),
):
    check_token(session_token, router.access_token_session)
    if format is not None:
        if format == "json":
            return JSONResponse(
                content={"message": "Welcome!"}, status_code=status.HTTP_200_OK
            )
        elif format == "html":
            return HTMLResponse(
                content="<h1>Welcome!</h1>", status_code=status.HTTP_200_OK
            )
    return PlainTextResponse(content="Welcome!", status_code=status.HTTP_200_OK)


@router.get("/welcome_token")
def welcome_token(
    response: Response, token: str = Query(None), format: str = Query(None)
):
    check_token(token, router.access_token_token)
    if format is not None:
        if format == "json":
            return JSONResponse(
                content={"message": "Welcome!"}, status_code=status.HTTP_200_OK
            )
        elif format == "html":
            return HTMLResponse(
                content="<h1>Welcome!</h1>", status_code=status.HTTP_200_OK
            )
    return PlainTextResponse(content="Welcome!", status_code=status.HTTP_200_OK)


@router.delete("/logout_session")
def logout_session(
    response: Response, format: str = Query(None), session_token: str = Cookie(None)
):
    check_token(session_token, router.access_token_session)
    remove_session_token(session_token, router.access_token_session)
    return RedirectResponse(
        "/logged_out?&format={}".format(format), status_code=status.HTTP_303_SEE_OTHER
    )


@router.delete("/logout_token")
def logout_token(
    response: Response, token: str = Query(None), format: str = Query(None)
):
    check_token(token, router.access_token_token)
    remove_session_token(token, router.access_token_token)
    return RedirectResponse(
        "/logged_out?&format={}".format(format), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logged_out")
def full_logout(response: Response, format: str = Query(None)):
    if format is not None:
        if format == "json":
            return JSONResponse(
                content={"message": "Logged out!"}, status_code=status.HTTP_200_OK
            )
        elif format == "html":
            return HTMLResponse(
                content="<h1>Logged out!</h1>", status_code=status.HTTP_200_OK
            )
    return PlainTextResponse(content="Logged out!", status_code=status.HTTP_200_OK)
