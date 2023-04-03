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
        "name": "subnet1",
        "description": "string",
    }
):
    response = client.post("/subnets/", json=json)
    assert response.status_code == 201
#    assert response.json() == {
#        "ip_v4": "192.168.0.0/24",
#        "ip_v6": None,
#        "mask": "string",
#        "name": "subnet1",
#        "description": "string",
#        "id": 1,
#        "addresses": []
#    }


def test_create_bad_name_subnet(
    json = {
        "ip_v4": "192.168.0.1/24",
        "mask": "mask",
        "name": "subnet1",
        "description": "string",
    }
):
    response = client.post("/subnets/", json=json)
    assert response.status_code == 422


def test_read_subnet_by_id():
    id = 1
    response = client.get(f"/subnets/{id}")
    assert response.status_code == 200


def test_read_subnet_by_bad_id():
    id = 2
    response = client.get(f"/subnets/{id}")
    assert response.status_code == 404


def test_delete_subnet():
    id = 1
    response = client.delete(f"/subnets/{id}")

    assert response.status_code == 204