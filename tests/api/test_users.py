from fastapi.testclient import TestClient
from webapp.main import app

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
