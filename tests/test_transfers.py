from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_transfers():
    response = client.get("/list_transfer")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_transfer():
    transfer_data = {
        "value": 1,
        "payer": 2,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Transferência realizada com sucesso"}

def test_transfer_payer_not_found():
    transfer_data = {
        "value": 1,
        "payer": 999,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário pagador não encontrado"}

def test_transfer_payee_not_found():
    transfer_data = {
        "value": 1,
        "payer": 2,
        "payee": 999
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário recebedor não encontrado"}

def test_transfer_insufficient_balance():
    transfer_data = {
        "value": 1000,
        "payer": 2,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Saldo insuficiente"}

def test_transfer_unauthorized():
    transfer_data = {
        "value": 1001,
        "payer": 1,
        "payee": 3
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Transação não autorizada"}

def test_transfer_common_user():
    transfer_data = {
        "value": 1,
        "payer": 3,
        "payee": 2
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Lojista não pode realizar pagamentos"}

def test_transfer_same_user():
    transfer_data = {
        "value": 1,
        "payer": 2,
        "payee": 2
    }
    response = client.post("/transfer", json=transfer_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Não é permitido transferir para a mesma conta"}