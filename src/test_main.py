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
    assert response.json() == {"message": "Usuário criado com sucesso"}

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
    response = client.post("/deposit?id=1&value=1")
    print(response)
    assert response.status_code == 200
    assert response.json() == {"message": "Depósito realizado com sucesso"}

def test_get_user():
    response = client.get(f"/users/1")
    print(response)
    assert response.status_code == 200
    user_test = {
        "id": 1,
        "full_name": "Test1 User",
        "email": "testuser1@example.com",
        "password": "9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05",
        "user_type": "comum",
        "document": "74384734108",
        "balance": response.json()["balance"]
    }
    assert response.json() == user_test

def test_get_user_not_found():
    response = client.get(f"/users/999")
    print(response)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário não encontrado"}

def test_transfer_payer_not_found():
    transfer_data = {
        "value": 1,
        "payer": 999,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário pagador não encontrado"}

def test_transfer_payee_not_found():
    transfer_data = {
        "value": 1,
        "payer": 2,
        "payee": 999
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário recebedor não encontrado"}

def test_transfer_insufficient_balance():
    transfer_data = {
        "value": 1000,
        "payer": 2,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 400
    assert response.json() == {"detail": "Saldo insuficiente"}

def test_transfer_unauthorized():
    transfer_data = {
        "value": 2000,
        "payer": 2,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 400
    assert response.json() == {"detail": "Transação não autorizada"}

def test_transfer_common_user():
    transfer_data = {
        "value": 1,
        "payer": 3,
        "payee": 2
    }
    response = client.post("/transfer", json=transfer_data)
    print(response)
    assert response.status_code == 400
    assert response.json() == {"detail": "Lojista não pode realizar pagamentos"}



