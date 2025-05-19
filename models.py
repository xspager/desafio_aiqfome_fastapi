from typing import Optional
import uuid

from email_validator import EmailNotValidError
from pydantic import EmailStr
from sqlmodel import Column, Field, SQLModel, String


class Product(SQLModel, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pass


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    email: str


class ClientBase(SQLModel):
    name: str
    email: EmailStr = Field(unique=True)


class Client(ClientBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)


class ClientCreate(ClientBase):
    pass
