import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_users():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_transfers():
    response = client.get("/transfers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    user_data = {
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword",
        "user_type": "comum",
        "balance": 0.0,
        "document": "74384744108"
    }
    response = client.post("/users", json=user_data)
    print(response.json())
    assert response.status_code == 200
    user = response.json()
    assert user["full_name"] == user_data["full_name"]
    assert user["email"] == user_data["email"]
    assert user["user_type"] == user_data["user_type"]
    assert user["balance"] == user_data["balance"]