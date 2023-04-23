from fastapi.testclient import TestClient

from fastipam.main import app


client = TestClient(app)


def test_read_nonexistent_subnets():
    response = client.get("/subnets/")
    assert response.status_code == 204


def test_create_ipv4_subnet(
    json = {
        "ip_v4": "192.168.0.0/24",
        "mask": "mask",
        "name": "api_test_subnet",
        "description": "string",
    }
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 201


def test_create_bad_name_subnet(
    json = {
        "ip_v4": "192.168.1.0/24",
        "mask": "mask",
        "name": "api_test_subnet",
        "description": "string",
    }
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 400


def test_read_subnet_by_id():
    id = 1
    response = client.get(f"/subnets/{id}")

    assert response.status_code == 200

def test_create_host(
    json = {
        "name": "api_test_subnet",
        "description": "string",
        "subnet_id": 1,
    }
):
    response = client.post("/addresses/", json=json)

    assert response.status_code == 201


def test_delete_host():
    id = 1
    response = client.delete(f"/addresses/{id}")

    assert response.status_code == 204


def test_read_subnet_by_bad_id():
    id = 99
    response = client.get(f"/subnets/{id}")

    assert response.status_code == 404


def test_delete_subnet():
    id = 1
    response = client.delete(f"/subnets/{id}")

    assert response.status_code == 204