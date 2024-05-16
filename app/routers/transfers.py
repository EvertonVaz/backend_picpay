from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.dependencies.database import get_db_connection
from app.models.models import Transactions, save_transaction
from app.routers.users import get_user_by_id, Users
from datetime import datetime
from random import randint
from time import sleep

transfers_router = APIRouter()

@transfers_router.get("/list_transfer")
async def list_transfers():
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    return cursor.fetchall()

# TODO: estudar e aplicar mocks
async def simulate_external_authorization(transaction: Transactions):
    sleep(1)
    if (randint(0, 9) > 8):
        return {"approved": False}
    return {"approved": True}

async def send_notification(email: str, value: float, message: str):
    print(f"Enviando notificação para {email}: {message} - Valor: R$ {value}")

async def update_user_balance(id: int, new_balance: float):
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, id))
    conn.commit()
    conn.close()

async def make_transfer(payer: Users, payee: Users, transaction: Transactions, approved: bool):
    new_balance_payer = payer["balance"] - transaction.value * approved
    new_balance_payee = payee["balance"] + transaction.value * approved
    await update_user_balance(transaction.payer, new_balance_payer)
    await update_user_balance(transaction.payee, new_balance_payee)
    transaction.status = "confirmada" if approved else "revertida"
    transaction.created_at = datetime.now()
    return transaction

@transfers_router.post("/transfer")
async def transfer(transaction: Transactions):
    trans = next(get_db_connection()).cursor().execute("SELECT * FROM transactions").fetchall()
    transaction.id = len(trans) + 1
    if transaction.value <= 0:
        raise HTTPException(status_code=400, detail="O valor da transferência deve ser positivo")

    if transaction.payer == transaction.payee:
        raise HTTPException(status_code=400, detail="Não é permitido transferir para a mesma conta")

    payer = await get_user_by_id(transaction.payer, type="comum")
    if not payer:
        raise HTTPException(status_code=404, detail="Usuário pagador não encontrado")

    payee = await get_user_by_id(transaction.payee)
    if not payee:
        raise HTTPException(status_code=404, detail="Usuário recebedor não encontrado")

    if payer["balance"] < transaction.value:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    if transaction.value > 1000:
        raise HTTPException(status_code=400, detail="Valor acima do permitido")

    transaction = await make_transfer(payer, payee, transaction, True)

    response = await simulate_external_authorization(transaction)
    if not response["approved"]:
        await save_transaction(await make_transfer(payer, payee, transaction, False))
        return JSONResponse({"message": "Transferência não autorizada"})

    await save_transaction(transaction)
    await send_notification(payer["email"], transaction.value, "transferência enviada")
    await send_notification(payee["email"], transaction.value, "transferência recebida")

    return JSONResponse({"message": "Transferência realizada com sucesso"})

