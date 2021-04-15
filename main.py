from fastapi import FastAPI, Response, Body, Request
from pydantic import BaseModel
import hashlib
from datetime import timedelta, date
from typing import Optional


app = FastAPI()
app.counter = 0

app.fake_datebase = {}
start = date.today()


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
    hashed_password = hashlib.sha512(password.encode())
    if hashed_password.hexdigest() == password_hash:
        response.status_code = 204
    else:
        response.status_code = 401


@app.post("/register/", response_model=RegisteredPerson)
async def register(person: Person, response: Response, request: Request):
    response.status_code = 201
    n_of_letters = 0
    for letter in person.name+person.surname:
        if (65<=ord(letter)<=90) or (97<=ord(letter)<=122):
            n_of_letters+=1 
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
