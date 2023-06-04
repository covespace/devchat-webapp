from fastapi.testclient import TestClient
from webapp.main import app
from webapp.controller import create_access_key, create_user, create_organization
from webapp.controller import add_user_to_organization
from webapp.utils import hash_access_key

client = TestClient(app)


def test_create_user(database):  # pylint: disable=W0613
    response = client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "testuser@example.com"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully."
    assert isinstance(response.json()["user_id"], int)


def test_create_user_invalid_email(database):  # pylint: disable=W0613
    response = client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "invalid_email"
    })
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid email provided."


def test_get_user_profile(database):  # pylint: disable=W0613
    # Create a test user
    user_response = client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "testuser@example.com"
    })
    user_id = user_response.json()["user_id"]

    response = client.get(f"/api/v1/users/{user_id}/profile")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "testuser@example.com"


def test_get_user_profile_not_found(database):  # pylint: disable=W0613
    user_id = 1  # Non-existent user_id
    response = client.get(f"/api/v1/users/{user_id}/profile")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_login(database):
    user = create_user(database, username="testuser", email="testuser@example.com")
    org = create_organization(database, name="Test-Org", country_code="US")
    add_user_to_organization(database, user.id, org.id)

    # Create an access key for the user
    _, value = create_access_key(database, user_id=user.id, organization_id=org.id)

    response = client.post("/api/v1/login", json={
        "key": value
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.json()["user_id"] == user.id

    response = client.post("/api/v1/login", json={
        "key": value.replace('e', 'a')
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid key hash"


def test_get_user_organizations(database):
    # Create a test user
    user = create_user(database, username="testuser", email="testuser@example.com")

    # Create two test organizations
    org1 = create_organization(database, name="Test-Org-1", country_code="US")
    org2 = create_organization(database, name="Test-Org-2", country_code="US")

    # Add the user to both organizations
    add_user_to_organization(database, user.id, org1.id)
    add_user_to_organization(database, user.id, org2.id)

    key1, _ = create_access_key(database, user_id=user.id, organization_id=org1.id)
    key2, _ = create_access_key(database, user_id=user.id, organization_id=org2.id)
    key3, _ = create_access_key(database, user_id=user.id, organization_id=org2.id)

    # Test the get_user_organizations_endpoint
    response = client.get(f"/api/v1/users/{user.id}/organizations")
    assert response.status_code == 200
    assert len(response.json()) == 2

    for org in response.json():
        if org["org_id"] == org1.id:
            assert org["org_name"] == org1.name
            assert org["role"] == "member"
            assert len(org["keys"]) == 1
            assert org["keys"][0]["thumbnail"] == key1.thumbnail
        elif org["org_id"] == org2.id:
            assert org["org_name"] == org2.name
            assert org["role"] == "member"
            assert len(org["keys"]) == 2
            assert org["keys"][0]["thumbnail"] == key2.thumbnail
            assert org["keys"][1]["thumbnail"] == key3.thumbnail
        else:
            assert False, "Unexpected organization ID"


def test_get_user_organizations_empty(database):
    # Create a test user
    user = create_user(database, username="testuser", email="testuser@example.com")

    # Test the get_user_organizations_endpoint with no organizations
    response = client.get(f"/api/v1/users/{user.id}/organizations")
    assert response.status_code == 200
    assert len(response.json()) == 0
