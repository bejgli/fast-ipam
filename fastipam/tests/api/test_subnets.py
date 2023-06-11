# from fastipam.tests.conftest import client


# Validation errors
def test_create_bad_ip(
    client,
    json={
        "subnet": {
            "ip": "notanip",
            "name": "api_test_subnet",
            "description": "string",
            "location": "westeu",
            "threshold": 0,
        },
        "reserve": 0,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 422


def test_create_missing_field(
    client,
    json={
        "subnet": {
            "ip": "192.168.0.0/24",
            "description": "string",
            "location": "westeu",
            "threshold": 0,
        },
        "reserve": 0,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 422


def test_create_threshold_invalid(
    client,
    json={
        "subnet": {
            "ip": "192.168.0.0/24",
            "name": "test",
            "description": "string",
            "location": "westeu",
            "threshold": 999,
        },
        "reserve": 0,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 422


def test_create_reserve_invalid(
    client,
    json={
        "subnet": {
            "ip": "192.168.0.0/24",
            "name": "test",
            "description": "string",
            "location": "westeu",
            "threshold": 500,
        },
        "reserve": 999,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 422


# Successfull creation
def test_create_empty_ipv4(
    client,
    json={"subnet": {"name": "empty_ipv4", "ip": "192.168.0.0/24"}},
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "empty_ipv4"
    assert data["ip"] == "192.168.0.0/24"
    assert "id" in data
    empty_ipv4_id = data["id"]


def test_create_empty_ipv6(
    client,
    json={
        "subnet": {
            "name": "empty_ipv6",
            "ip": "fe80::1234",
        }
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "empty_ipv6"
    assert data["ip"] == "fe80::1234"
    assert "id" in data
    empty_ipv4_id = data["id"]


def test_create_reserve_ipv6_bad_reserve(
    client,
    json={
        "subnet": {
            "name": "reserve_ipv6",
            "ip": "2001:0db8:1234:5678::/64",
        },
        "reserve": 99,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 422


def test_create_reserve_ipv6(
    client,
    json={
        "subnet": {
            "name": "reserve_ipv6",
            "ip": "2001:0db8:1234:5678::/64",
        },
        "reserve": 5,
    },
):
    response = client.post("/subnets/", json=json)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "reserve_ipv6"
    assert data["ip"] == "2001:0db8:1234:5678::/64"
    assert "id" in data
    reserve_ipv6_id = data["id"]
    assert len(data["hosts"]) == 5


def test_read_all_subnets(client):
    response = client.get("/subnets/")
    assert response.status_code == 204


# Conflict checks
# def test_create_bad_name_subnet(
#    client,
#    json={
#        "subnet": {
#            "ip": "192.168.1.0/24",
#            "name": "api_test_subnet",
#            "description": "string",
#            "location": "westeu",
#            "threshold": 0,
#        },
#        "reserve": 0,
#    },
# ):
#    response = client.post("/subnets/", json=json)
#
#    assert response.status_code == 400

#
# def test_create_subnet_with_supernet(
#    client,
#    json={
#        "subnet": {
#            "ip": "192.168.0.0/26",
#            "name": "nested_subnet",
#            "supernet": 1,
#        },
#        "reserve": 0,
#    },
# ):
#    response = client.post("/subnets/", json=json)
#
#    assert response.status_code == 201
#
#
# def test_mismatch_subnet_versions(
#    client,
#    json={
#        "subnet": {
#            "ip": "fe80::1234",
#            "name": "mismatch_versions",
#            "supernet": 1,
#        },
#        "reserve": 0,
#    },
# ):
#    response = client.post("/subnets/", json=json)
#
#    assert response.status_code == 400
#
#
# def test_update_subnet(
#    client,
#    json={
#        "name": "updated_subnet_name",
#        "description": "updated_description",
#        "location": "easteu",
#        "threshold": 50,
#    },
# ):
#    id = 1
#    response = client.patch(f"/subnets/{id}", json=json)
#
#    assert response.status_code == 200
#
#
# def test_read_subnet_by_id(client):
#    id = 1
#    response = client.get(f"/subnets/{id}")
#
#    assert response.status_code == 200
#
#
# def test_create_host(
#    client,
#    json={
#        "name": "api_test_host",
#        "description": "string",
#        "subnet_id": 1,
#    },
# ):
#    response = client.post("/hosts/", json=json)
#
#    assert response.status_code == 201
#
#
# def test_update_host(
#    client,
#    json={
#        "name": "new name",
#        "description": "new description",
#    },
# ):
#    id = 1
#    response = client.patch(f"/hosts/{id}", json=json)
#
#    assert response.status_code == 200
#
#
# def test_delete_host(client):
#    id = 1
#    response = client.delete(f"/hosts/{id}")
#
#    assert response.status_code == 204
#
#
# def test_read_subnet_by_bad_id(client):
#    id = 99
#    response = client.get(f"/subnets/{id}")
#
#    assert response.status_code == 404
#
#
# def test_delete_subnet(client):
#    id = 1
#    response = client.delete(f"/subnets/{id}")
#
#    assert response.status_code == 204
#
#    id = 2
#    response = client.delete(f"/subnets/{id}")
#
#    assert response.status_code == 204
#
