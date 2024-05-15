from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.routers.transfers import update_user_balance
from app.models.models import Transactions, save_transaction
from app.routers.users import get_user_by_id
from datetime import datetime

deposit_router = APIRouter()

@deposit_router.post("/deposit")
async def deposit(id: int, value: float):
	user = await get_user_by_id(id)
	print(user)
	if not user:
		raise HTTPException(status_code=404, detail="Usuário não encontrado")
	if value <= 0:
		raise HTTPException(status_code=400, detail="O valor do depósito deve ser positivo")
	new_balance = user["balance"] + value
	await update_user_balance(id, new_balance)
	transaction = Transactions(payer=id, payee=id, value=value, status="confirmed", date=datetime.now())
	await save_transaction(transaction)
	return JSONResponse({"message": "Depósito realizado com sucesso"})