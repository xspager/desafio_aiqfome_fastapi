import uuid

from typing import List, Optional

from sqlmodel import Field, SQLModel

class Product(SQLModel, table=True):
    #id: int | None = Field(default=None, primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    pass

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    email: str
