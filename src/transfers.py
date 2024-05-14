from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from database import get_db_connection
from models import Transactions, save_transaction
from users import get_user_by_id
from datetime import datetime

transfers_router = APIRouter()

# TODO: estudar e aplicar mocks
async def simulate_external_authorization(value):
    if (value > 1000):
        return {"approved": False}
    return {"approved": True}

async def send_notification(email: str, value: float, message: str):
    print(f"Enviando notificação para {email}: {message} - Valor: R$ {value}")

async def update_user_balance(id: int, new_balance: float):
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, id))
    cursor.execute("SELECT id, balance FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

@transfers_router.get("/list_transfer")
async def list_transfers():
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    return cursor.fetchall()

@transfers_router.post("/transfer")
async def transfer(transaction: Transactions, request: Request):
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

@transfers_router.post("/deposit")
async def deposit(id: int, value: float):
    user = await get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    new_balance = user["balance"] + value
    await update_user_balance(id, new_balance)
    transaction = Transactions(payer=id, payee=id, value=value, status="confirmed", date=datetime.now())
    await save_transaction(transaction)
    return JSONResponse({"message": "Depósito realizado com sucesso"})

