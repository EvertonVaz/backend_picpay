from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
from starlette.responses import JSONResponse
from models import Users, Transactions, save_transaction, save_user
from database import get_db_connection, create_user_table, create_transaction_table
from datetime import datetime

app = FastAPI()

async def simulate_external_authorization(value):
    return {"approved": True}

async def update_user_balance(id: int, new_balance: float):
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, id))
    cursor.execute("SELECT id, balance FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

async def send_notification(email: str, value: float, message: str):
    print(f"Enviando notificação para {email}: {message} - Valor: R$ {value}")

@app.get("/")
async def list_users():
    create_user_table()
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

@app.get("/transfers")
async def list_transfers():
    create_transaction_table()
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    return cursor.fetchall()

async def get_user_by_id(id, type = None):
    users = next(get_db_connection()).cursor().execute("SELECT * FROM users").fetchall()
    for user in users:
        if id == user["id"]:
            if type:
                if user["user_type"] == "comum":
                    return user
                else:
                    raise HTTPException(status_code=400, detail="Lojista não pode realizar pagamentos")
            else:
                return user
    return None

@app.post("/users")
async def create_user(user: Users):
    create_user_table()
    users = await list_users()
    user.id = len(users) + 1
    if user.user_type not in ["comum", "lojista"]:
        raise HTTPException(status_code=400, detail="Tipo de usuário inválido")
    if user.document in [u["document"] for u in users]:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado")
    if user.email in [u["email"] for u in users]:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    await save_user(user)
    return JSONResponse({"message": "Usuário criado com sucesso"})


@app.post("/transfer")
async def transfer(transaction: Transactions, request: Request):
    create_transaction_table()
    trans = next(get_db_connection()).cursor().execute("SELECT * FROM transactions").fetchall()
    transaction.id = len(trans) + 1
    # Verificar se o usuário pagador existe e é do tipo comum
    payer = await get_user_by_id(transaction.payer, type="comum")
    if not payer:
        raise HTTPException(status_code=404, detail="Usuário pagador não encontrado")

    # Verificar se o usuário recebedor existe
    payee = await get_user_by_id(transaction.payee)
    if not payee:
        raise HTTPException(status_code=404, detail="Usuário recebedor não encontrado")

    # Validar se o usuário pagador tem saldo suficiente
    if payer["balance"] < transaction.value:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    # Simular consulta à API externa (mock)
    response = await simulate_external_authorization(transaction.value)
    if not response["approved"]:
        raise HTTPException(status_code=400, detail="Transação não autorizada")

    # Realizar a transferência
    new_balance_payer = payer["balance"] - transaction.value
    new_balance_payee = payee["balance"] + transaction.value
    await update_user_balance(transaction.payer, new_balance_payer)
    await update_user_balance(transaction.payee, new_balance_payee)

    # Salvar a transação no banco de dados
    transaction.status = "confirmed"
    transaction.created_at = datetime.now()
    await save_transaction(transaction)

    # Enviar notificação para pagador e recebedor (mock)
    await send_notification(payer["email"], transaction.value, "transferência enviada")
    await send_notification(payee["email"], transaction.value, "transferência recebida")

    return JSONResponse({"message": "Transferência realizada com sucesso"})

@app.post("/deposit")
async def deposit(id: int, value: float):
    create_transaction_table()
    user = await get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    new_balance = user["balance"] + value
    await update_user_balance(id, new_balance)
    transaction = Transactions(payer=id, payee=id, value=value, status="confirmed", date=datetime.now())
    await save_transaction(transaction)
    return JSONResponse({"message": "Depósito realizado com sucesso"})
