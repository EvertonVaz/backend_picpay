from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.dependencies.database import conn
from app.models.models import Users, save_user


user_router = APIRouter()

@user_router.get("/")
async def list_users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

def check_commom_user(user: Users):
    if user["user_type"] == "comum":
        return user
    else:
        raise HTTPException(status_code=400, detail="Lojista não pode realizar pagamentos")

async def get_user_by_id(id, type = None):
    users = conn.cursor().execute("SELECT * FROM users").fetchall()
    for user in users:
        if id == user["id"]:
            if type:
                return check_commom_user(user)
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

@user_router.delete("/users/{id}")
async def delete_user(id: int):
    if not await get_user_by_id(id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    conn = conn
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    return JSONResponse({"message": "Usuário deletado com sucesso"})