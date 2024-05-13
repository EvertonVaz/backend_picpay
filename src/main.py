from fastapi import FastAPI
from database import create_user_table, create_transaction_table
from users import user_router
from transfers import transfers_router

app = FastAPI()
app.include_router(user_router)
app.include_router(transfers_router)
create_user_table()
create_transaction_table()




