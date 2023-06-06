from fastapi.testclient import TestClient

from fastipam.main import app


client = TestClient(app)


def test_read_nonexistent_subnets():
    response = client.get("/api/subnets/")
    assert response.status_code == 204


def test_create_ipv4_subnet(
    json={
        "ip": "192.168.0.0/24",
        "name": "api_test_subnet",
        "description": "string",
        "location": "westeu",
        "threshold": 0,
    }
):
    response = client.post("/api/subnets/", json=json)

    assert response.status_code == 201


def test_create_bad_name_subnet(
    json={
        "ip": "192.168.1.0/24",
        "name": "api_test_subnet",
        "description": "string",
        "location": "westeu",
        "threshold": 0,
    }
):
    response = client.post("/api/subnets/", json=json)

    assert response.status_code == 400


def test_create_subnet_with_supernet(
    json={"ip": "192.168.0.0/26", "name": "nested_subnet", "supernet": 1}
):
    response = client.post("/api/subnets/", json=json)

    assert response.status_code == 201


def test_mismatch_subnet_versions(
    json={"ip": "fe80::1234", "name": "mismatch_versions", "supernet": 1}
):
    response = client.post("/api/subnets/", json=json)

    assert response.status_code == 400


def test_update_subnet(
    json={
        "name": "updated_subnet_name",
        "description": "updated_description",
        "location": "easteu",
        "threshold": 50,
    }
):
    id = 1
    response = client.patch(f"/api/subnets/{id}", json=json)

    assert response.status_code == 200


def test_read_subnet_by_id():
    id = 1
    response = client.get(f"/api/subnets/{id}")

    assert response.status_code == 200


def test_create_host(
    json={
        "name": "api_test_host",
        "description": "string",
        "subnet_id": 1,
    }
):
    response = client.post("/api/hosts/", json=json)

    assert response.status_code == 201


def test_update_host(
    json={
        "name": "new name",
        "description": "new description",
    }
):
    id = 1
    response = client.patch(f"/api/hosts/{id}", json=json)

    assert response.status_code == 200


def test_delete_host():
    id = 1
    response = client.delete(f"/api/hosts/{id}")

    assert response.status_code == 204


def test_read_subnet_by_bad_id():
    id = 99
    response = client.get(f"/api/subnets/{id}")

    assert response.status_code == 404


def test_delete_subnet():
    id = 1
    response = client.delete(f"/api/subnets/{id}")

    assert response.status_code == 204

    id = 2
    response = client.delete(f"/api/subnets/{id}")

    assert response.status_code == 204
