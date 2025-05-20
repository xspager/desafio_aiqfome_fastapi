from typing import List, Optional
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class ClientBase(SQLModel):
    email: EmailStr = Field(unique=True)
    name: str


class Client(ClientBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True)
    name: str
    favorites: list["Favorite"] = Relationship(back_populates="client")


class ClientCreate(ClientBase):
    pass


class ClientWithFavorites(ClientBase):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    favorites: List["FavoritePublic"] = []


class FavoriteBase(SQLModel):
    product_id: int
    client_id: uuid.UUID | None = Field(default=None, foreign_key="client.id")


class Favorite(FavoriteBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client: Client | None = Relationship(back_populates="favorites")

    __table_args__ = (UniqueConstraint("client_id", "product_id"),)


class FavoriteCreate(FavoriteBase):
    pass


class FavoritePublic(FavoriteBase):
    product_id: int
    title: str
    price: float
    description: str
    category: str
    image: str


class Review(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    text: str = Field(max_length=4000)
