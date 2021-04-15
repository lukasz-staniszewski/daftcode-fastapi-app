from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
import hashlib
from datetime import timedelta, date

app = FastAPI()
app.counter = 0

app.fake_datebase = {}


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
async def read_items(password: str, password_hash: str, response: Response):
    hashed_password = hashlib.sha512(password.encode())
    if password == "":
        response.status_code = 401
    if hashed_password.hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post("/register/", response_model=RegisteredPerson)
async def register(person: Person, response: Response):
    response.status_code = 201
    n_of_letters = len(person.name) + len(person.surname)
    app.counter += 1
    date_then = date.today() + timedelta(days=n_of_letters)
    app.fake_datebase[app.counter] = RegisteredPerson(
        id=app.counter, name=person.name, surname=person.surname, register_date=str(date.today()), vaccination_date=str(date_then))
    return RegisteredPerson(id=app.counter, name=person.name, surname=person.surname, register_date=str(date.today()), vaccination_date=str(date_then))


@app.get("/patient/{patient_id}", response_model=RegisteredPerson)
async def getpatient(patient_id: int, response: Response):
    if patient_id < 1:
        response.status_code = 400
    elif patient_id >= app.counter:
        response.status_code = 404
    else:
        response.status_code = 200
        return app.fake_datebase[patient_id]
