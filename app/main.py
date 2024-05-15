from fastapi import FastAPI
from app.dependencies.database import create_user_table, create_transaction_table
from app.routers.users import user_router
from app.routers.transfers import transfers_router
from app.routers.deposit import deposit_router

app = FastAPI()
app.include_router(user_router)
app.include_router(transfers_router)
app.include_router(deposit_router)
create_user_table()
create_transaction_table()


