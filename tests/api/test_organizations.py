from fastapi.testclient import TestClient
from webapp.main import app

client = TestClient(app)


def test_create_organization(database):  # pylint: disable=W0613
    response = client.post("/api/v1/organizations", json={"name": "Test-Org"})
    assert response.status_code == 201
    assert response.json()["message"] == "Organization created successfully."
    assert "org_id" in response.json()


def test_create_org_invalid_name(database):  # pylint: disable=W0613
    invalid_org_name = "Invalid@Org#Name"
    country_code = "US"

    response = client.post(
        "/api/v1/organizations",
        json={"name": invalid_org_name, "country_code": country_code},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid organization name provided."


def test_list_users(database):  # pylint: disable=W0613
    # Create a test organization using the create_organization API
    org_response = client.post("/api/v1/organizations",
                               json={"name": "Test-Org", "country_code": "US"})
    org_id = org_response.json()["org_id"]

    # Test case: No users in the organization
    response = client.get(f"/api/v1/organizations/{org_id}/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

    # Test case: Users exist in the organization
    # Add users to the organization using the add_user API
    user1 = {"username": "User1", "email": "user1@example.com"}
    user2 = {"username": "User2", "email": "user2@example.com"}
    response1 = client.post("/api/v1/users", json=user1)
    response2 = client.post("/api/v1/users", json=user2)
    user1_id = response1.json()["user_id"]
    user2_id = response2.json()["user_id"]

    # Add the created users to the organization
    response1 = client.post(f"/api/v1/organizations/{org_id}/users",
                            json={"user_id": user1_id, "role": "owner"})
    response2 = client.post(f"/api/v1/organizations/{org_id}/users",
                            json={"user_id": user2_id, "role": "member"})
    assert response1.status_code == 200
    assert response2.status_code == 200

    response = client.get(f"/api/v1/organizations/{org_id}/users")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["username"] == "User1"
    assert response.json()[0]["email"] == "user1@example.com"
    assert response.json()[1]["username"] == "User2"
    assert response.json()[1]["email"] == "user2@example.com"


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
    assert response.status_code == 200
    assert response.json()["message"] == "Access key issued and sent to the user by email."
    assert "key_hash" in response.json()
