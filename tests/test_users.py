from fastapi.testclient import TestClient
from app.main import app
import random

client = TestClient(app)


def test_list_users():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    n = str(random.randint(1, 100000))
    user_data = {
        "full_name": f"Teste{n} User",
        "email": f"testuser{n}@example.com",
        "password": "testpassword",
        "user_type": "comum",
        "balance": 0.0,
        "document": f"{random.randint(10000000000, 99999999999)}"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Usuário criado com sucesso"}

def test_delete_user():
    response = client.post("/users/5")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Usuário deletado com sucesso"}

def test_get_user():
    response = client.get(f"/users/1")
    assert response.status_code == 200
    user_test = {
        "id": 1,
        "full_name": "string",
        "email": "user@example.com",
        "password": "38ce7d24f32e00348c635b52797b618aa23c46865f38755b9a3124a3a8c57e1f",
        "user_type": "comum",
        "document": "34710107018",
        "balance": response.json()["balance"]
    }
    assert response.json() == user_test

def test_get_user_not_found():
    response = client.get(f"/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário não encontrado"}
