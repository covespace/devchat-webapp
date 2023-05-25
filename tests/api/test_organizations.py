from fastapi.testclient import TestClient
from webapp.main import app


client = TestClient(app)


def test_create_organization(database):  # pylint: disable=W0613
    response = client.post("/api/v1/organizations", json={"name": "Test Org", "country_code": "US"})
    assert response.status_code == 201
    assert response.json()["message"] == "Organization created successfully."
    assert "org_id" in response.json()


def test_list_users(database):  # pylint: disable=W0613
    # Create a test organization using the create_organization API
    org_response = client.post("/api/v1/organizations",
                               json={"name": "Test Org", "country_code": "US"})
    org_id = org_response.json()["org_id"]

    response = client.get(f"/api/v1/organizations/{org_id}/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
