from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.dependencies.database import get_db_connection, create_transaction_table, create_user_table
from hashlib import sha256


class UserBase(BaseModel):
    id: int = Field(default=0, title="ID do usuário")
    full_name: str = Field(max_length=255, title="Nome completo do usuário")
    email: EmailStr = Field(title="Endereço de e-mail do usuário")
    password: str = Field(min_length=8, title="Senha do usuário")
    user_type: str = Field(title="Tipo de usuário (comum ou lojista)", json_schema_extra={'enum': ["comum", "lojista"]})
    balance: float = Field(default=0.0, title="Saldo do usuário")
    dict(from_attributes = True)

class CommonUser(UserBase):
    document: str = Field(max_length=11, min_length=11, pattern=r"\d{11}", title="CPF do usuário")

class ShopUser(UserBase):
    document: str = Field(max_length=14, min_length=14, pattern=r"\d{14}", title="CNPJ do usuário")

class Transactions(BaseModel):
    id: int = Field(default=0, title="ID da transação")
    value: float = Field(gt=0, title="Valor da transação")
    payer: int = Field(title="ID do usuário pagador")
    payee: int = Field(title="ID do usuário recebedor")
    created_at: datetime = Field(default=datetime.now, title="Data e hora da transação")
    status: str = Field(default="pendente", json_schema_extra={'enum': ["pendente", "confirmada", "revertida"]}, title="Status da transação")
    dict(from_attributes = True)

Users = CommonUser | ShopUser

async def save_user(user: Users):
    conn = next(get_db_connection())
    create_user_table()
    cursor = conn.cursor()
    # Inserção do novo usuário na tabela
    cursor.execute(
        """
        INSERT INTO users (
            id,
            full_name,
            email,
            password,
            user_type,
            document,
            balance
        ) VALUES (
            :id,
            :full_name,
            :email,
            :password,
            :user_type,
            :document,
            :balance
        )
        """,
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "password": sha256(user.password.encode()).hexdigest(),
            "user_type": user.user_type,
            "document": user.document,
            "balance": 0.0,
        },
    )
    conn.commit()
    return True


async def save_transaction(transaction: Transactions):
    conn = next(get_db_connection())
    create_transaction_table()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (
            payer_id,
            payee_id,
            value,
            status,
            created_at
        ) VALUES (
            :payer_id,
            :payee_id,
            :value,
            :status,
            :created_at
        )
        """,
        {
            "id": transaction.id,
            "payer_id": transaction.payer,
            "payee_id": transaction.payee,
            "value": transaction.value,
            "status": transaction.status,
            "created_at": datetime.now(),
        },
    )
    conn.commit()
    return True
