import pytest
from main import app
# from models import Users, Transactions, save_transaction, save_user
from fastapi.testclient import TestClient

client = TestClient(app)

def test_list_users():
    response = client.get("/")
    print(response)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_transfers():
    response = client.get("/list_transfer")
    print(response)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

#TODO: estudar e aplicar mocks
def test_create_user():
    global client_id
    user_data = {
        "full_name": "Test1 User",
        "email": "testuser1@example.com",
        "password": "testpassword",
        "user_type": "comum",
        "balance": 0.0,
        "document": "74384734108"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 200
    #implementar o delete e testar ele aqaui tbm

def test_delete_user():
    response = client.post("/users/5")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Usuário deletado com sucesso"}

def test_create_transfer():
    transfer_data = {
        "value": 1,
        "payer": 2,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Transferência realizada com sucesso"}

def test_create_deposit():
    response = client.post("/deposit?id=2&value=1")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Depósito realizado com sucesso"}

def test_get_user():
    response = client.get(f"/users/1")
    print(response)
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "full_name": "string",
        "email": "user@example.com",
        "password": "38ce7d24f32e00348c635b52797b618aa23c46865f38755b9a3124a3a8c57e1f",
        "user_type": "comum",
        "document": "34710107018",
        "balance": response.json()["balance"]
    }
