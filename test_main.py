from fastapi.testclient import TestClient
import pytest
from main import app
from datetime import date, timedelta

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}


@pytest.mark.parametrize("name", ["Zenek", "Marek", "Alojzy Niezdąży"])
def test_hello_name(name):
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.json() == {"msg": f"Hello {name}"}


def test_methods():
    responseget = client.get("/method")
    assert responseget.status_code == 200
    assert responseget.json() == {"method": "GET"}

    responseput = client.put("/method")
    assert responseput.status_code == 200
    assert responseput.json() == {"method": "PUT"}

    responsepost = client.post("/method")
    assert responsepost.status_code == 201
    assert responsepost.json() == {"method": "POST"}

    responsedelete = client.delete("/method")
    assert responsedelete.status_code == 200
    assert responsedelete.json() == {"method": "DELETE"}

    responseoptions = client.options("/method")
    assert responseoptions.status_code == 200
    assert responseoptions.json() == {"method": "OPTIONS"}


def test_auth():
    response = client.get(
        "/auth/?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215")
    assert response.status_code == 204

    response = client.get(
        "/auth/?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091")
    assert response.status_code == 401

    response = client.get("/auth/?password&password_hash")
    assert response.status_code == 401


def test_register():
    date_today = date.today()
    response = client.post(
        "/register/", json={"name": "Lukasz", "surname": "Staniszewski"})
    assert response.status_code == 201
    date_then = date_today + timedelta(days=18)
    assert response.json() == {"id": 1, "name": "Lukasz", "surname": "Staniszewski",
                               "register_date": f"{date_today}", "vaccination_date": f"{date_then}"}

    response = client.post(
        "/register/", json={"name": "Marcin", "surname": "Najman"})
    assert response.status_code == 201
    date_then = date_today + timedelta(days=12)
    assert response.json() == {"id": 2, "name": "Marcin", "surname": "Najman",
                               "register_date": f"{date_today}", "vaccination_date": f"{date_then}"}

    response = client.post(
        "/register/", json={"name": "Krzysztof", "surname": "Kolumb"})
    assert response.status_code == 201
    date_then = date_today + timedelta(days=15)
    assert response.json() == {"id": 3, "name": "Krzysztof", "surname": "Kolumb",
                               "register_date": f"{date_today}", "vaccination_date": f"{date_then}"}

    response = client.post(
        "/register/", json={"name": "Krzysztof", "surname": "Kolumb"})
    assert response.status_code == 201
    date_then = date_today + timedelta(days=15)
    assert response.json() != {"id": 5, "name": "Krzysztof", "surname": "Kolumb",
                               "register_date": f"{date_today}", "vaccination_date": f"{date_then}"}


def test_patient():
    date_today = date.today()
    response_post = client.post(
        "/register/", json={"name": "Lukasz", "surname": "Staniszewski"})
    assert response_post.status_code == 201
    date_then = date_today + timedelta(days=18)

    response_get = client.get("/patient/1")
    assert response_get.status_code == 200
    assert response_get.json() == {"id": 1, "name": "Lukasz", "surname": "Staniszewski",
                                   "register_date": f"{date_today}", "vaccination_date": f"{date_then}"}

    response_get2 = client.get("/patient/8")
    assert response_get2.status_code == 404

    response_get3 = client.get("patient/-1")
    assert response_get3.status_code == 400
