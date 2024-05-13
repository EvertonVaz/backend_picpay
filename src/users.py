from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from database import get_db_connection
from models import Users, save_user

user_router = APIRouter()

@user_router.get("/")
async def list_users():
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
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

@user_router.get("/users/{id}")
async def get_user(id: int):
    user = await get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@user_router.post("/users")
async def create_user(user: Users):
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

@user_router.post("/users/{id}")
async def delete_user(id: int):
    conn = next(get_db_connection())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    return JSONResponse({"message": "Usuário deletado com sucesso"})