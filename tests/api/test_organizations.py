from fastapi.testclient import TestClient
from webapp.main import app


client = TestClient(app)


def test_create_organization(database):  # pylint: disable=W0613
    response = client.post("/api/v1/organizations", json={"name": "Test-Org", "country_code": "US"})
    assert response.status_code == 201
    assert response.json()["message"] == "Organization created successfully."
    assert "org_id" in response.json()


def test_list_users(database):  # pylint: disable=W0613
    # Create a test organization using the create_organization API
    org_response = client.post("/api/v1/organizations",
                               json={"name": "Test-Org", "country_code": "US"})
    org_id = org_response.json()["org_id"]

    response = client.get(f"/api/v1/organizations/{org_id}/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_user_to_organization(database):  # pylint: disable=W0613
    # Create a test user using the create_user API
    user_response = client.post("/api/v1/users", json={
        "username": "testuser",
        "email": "testuser@example.com"
    })
    user_id = user_response.json()["user_id"]

    # Create a test organization using the create_organization API
    org_response = client.post("/api/v1/organizations",
                               json={"name": "Test-Org", "country_code": "US"})
    org_id = org_response.json()["org_id"]

    # Add the created user to the organization
    response = client.post(f"/api/v1/organizations/{org_id}/users",
                           json={"user_id": user_id, "role": "owner"})
    assert response.status_code == 200
    assert response.json()["message"] == "User added to the organization successfully."


def test_issue_access_key(database):  # pylint: disable=W0613
    # Create a test user using the create_user API
    user_response = client.post("/api/v1/users", json={
        "username": "test-merico-dev",
        "email": "test@merico.dev"
    })
    assert user_response.status_code == 201
    user_id = user_response.json()["user_id"]

    # Create a test organization using the create_organization API
    org_response = client.post("/api/v1/organizations",
                               json={"name": "Test-Org", "country_code": "US"})
    org_id = org_response.json()["org_id"]

    # Add the created user to the organization
    client.post(f"/api/v1/organizations/{org_id}/users",
                json={"user_id": user_id, "role": "owner"})

    # Issue an access key for the user in the organization
    response = client.post(f"/api/v1/organizations/{org_id}/user/{user_id}/access_key")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Access key issued and sent to the user by email."
    assert "key_hash" in response.json()
