# tests/test_deposit.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_deposit():
    response = client.post("/deposit?id=1&value=1000")
    assert response.status_code == 200
    assert response.json() == {"message": "Depósito realizado com sucesso"}

def test_create_deposit_negative_value():
    response = client.post("/deposit?id=1&value=-1000")
    assert response.status_code == 400
    assert response.json() == {"detail": "O valor do depósito deve ser positivo"}

def test_create_deposit_zero_value():
    response = client.post("/deposit?id=1&value=0")
    assert response.status_code == 400
    assert response.json() == {"detail": "O valor do depósito deve ser positivo"}

def test_create_deposit_invalid_id():
    response = client.post("/deposit?id=9999999&value=1000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuário não encontrado"}
