from fastapi import FastAPI, Response, Request, Query, HTTPException, Cookie, Depends, status
from pydantic import BaseModel
from hashlib import sha256, sha512
from datetime import timedelta, date
from typing import Optional, List
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi_mako import FastAPIMako
from routers.router import router
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
app.counter = 0
app.__name__ = "templates"
app.fake_datebase = {}
start = date.today()

mako = FastAPIMako(app)
templates = Jinja2Templates(directory="templates")

app.include_router(router, prefix="/v1", tags=["api_v1"])
app.include_router(router, tags=["default"])

objects = {
    1: {"field_a": "a", "field_b": "b"},
    2: {"field_a": "a", "field_b": "b"},
    3: {"field_a": "a", "field_b": "b"},
    # .... #
}

app.secret_key = "very constatn and random secret, best 64+ characters"
app.access_tokens = []

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


@app.get("/hello/{name}", response_model=HelloResp)
async def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get('/counter')
def counter():
    app.counter += 1
    return app.counter


@app.api_route("/method", methods=["GET", "POST", "DELETE", "OPTIONS", "PUT"])
def method(response: Response, request: Request):
    if str(request.method) == "POST":
        response.status_code = 201
    else:
        response.status_code = 200
    return {"method": str(request.method)}


@app.get("/auth/")
async def read_items(response: Response, password: Optional[str] = None, password_hash: Optional[str] = None):
    if password == "" or password_hash == "" or password is None or password_hash is None:
        response.status_code = 401
        return
    hashed_password = sha512(password.encode())
    if hashed_password.hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post("/register/", response_model=RegisteredPerson)
async def register(person: Person, response: Response, request: Request):
    response.status_code = 201
    n_of_letters = 0
    for letter in person.name + person.surname:
        if letter.isalpha():
            n_of_letters += 1
    app.counter += 1
    date_then = start + timedelta(days=n_of_letters)
    app.fake_datebase[app.counter] = RegisteredPerson(
        id=app.counter, name=person.name, surname=person.surname, register_date=str(start), vaccination_date=str(date_then))
    return RegisteredPerson(id=app.counter, name=person.name, surname=person.surname, register_date=str(start), vaccination_date=str(date_then))


@app.get("/patient/{patient_id}", response_model=RegisteredPerson)
async def getpatient(patient_id: int, response: Response):
    if patient_id < 1:
        response.status_code = 400
    elif patient_id > app.counter:
        response.status_code = 404
    else:
        response.status_code = 200
        return app.fake_datebase[patient_id]


@app.get("/request_query_string_discovery/")
def get_params(u: str = Query("default"), q: List[str] = Query(None)):
    query_items = {"q": q, "u": u}
    return query_items


@app.get("/static", response_class=HTMLResponse)
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


@app.get("/jinja")
def read_item(request: Request):
    return templates.TemplateResponse("index.html.j2", {
        "request": request, "my_string": "Wheeeee!", "my_list": [0, 1, 2, 3, 4, 5]})


@app.get("/mako", response_class=HTMLResponse)
@mako.template("index_mako.html")
def index_mako(request: Request):
    setattr(request, "mako", "test")
    return {"my_string": "Wheeeee!", "my_list": [0, 1, 2, 3, 4, 5]}


@app.get("/simple_path_tmpl/{sample_variable}/{sample_2}")
def simple_path_tmpl(sample_variable: str, sample_2: str):
    print(f"{sample_variable=}")
    print(type(sample_variable))
    return {"sample_variable": sample_variable, "sample_2": sample_2}


@app.get("/files/{file_path:path}/terminator/{x1}")
def read_file(file_path: str, x1: str):
    return {"file_path": file_path, "x1": x1}


@app.get("/simple_path_tmpl/{sample_variable}")
def simple_path_tmpl1(sample_variable: str):
    print(f"{sample_variable=}")
    print(type(sample_variable))
    return {"sample_variable": sample_variable}


@app.get("/simple_path_tmpl/{obj_id}/{field}")
def simple_path_tmpl2(obj_id: int, field: str):
    print(f"{obj_id=}")
    print(f"{field=}")
    return {"field": objects.get(obj_id, {}).get(field)}


@app.get("/items/")
def read_items(*, ads_id: str = Cookie(None)):
    return {"ads_id": ads_id}


@app.post("/cookie-and-object/")
def create_cookie(response: Response):
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return {"message": "Come to the dark side, we have cookies"}


@app.post("/login/")
def login(user: str, password: str, response: Response):
    session_token = sha256(f"{user}{password}{app.secret_key}".encode()).hexdigest()
    app.access_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return{"message": "Welcome"}


@app.get("/data/")
def secured_data(*, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=403, detail="Unauthorised")
    else:
        return {"message": "Secure content!!!"}


@app.get('/hello', response_class=HTMLResponse)
def hello():
    return f"<h1>Hello! Today date is {start}</h1>"


correct_login = "4dm1n"
correct_passwd = "NotSoSecurePa$$"
app.access_token_session = None
app.access_token_token = None


def check_usrnm_passwd(credentials):
    correct_usrnm = secrets.compare_digest(credentials.username, correct_login)
    correct_password = secrets.compare_digest(credentials.password, correct_passwd)
    if not (correct_usrnm and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised - incorrect login or password!",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.post('/login_session')
def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    check_usrnm_passwd(credentials)
    response.status_code = 201
    session_token = sha512("something_completely_random".encode()).hexdigest()
    app.access_token_session = session_token
    response.set_cookie(key="session_token", value=session_token)


@app.post('/login_token', response_class=JSONResponse)
def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    check_usrnm_passwd(credentials)
    response.status_code = 201
    token_value = sha512("something_more_completely_random".encode()).hexdigest()
    app.access_token_token = token_value
    return {"token": token_value}
