from typing import Any
from uuid import UUID

import httpx

from contextlib import asynccontextmanager

from sqlalchemy.exc import IntegrityError

from fastapi import Depends, FastAPI, Query, HTTPException, status
from sqlmodel import Session, select

from app.database import engine, create_db_and_tables
from app.models import (
    Client,
    ClientBase,
    ClientWithFavorites,
    Favorite,
    FavoriteCreate,
    FavoritePublic,
)


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

"""
Desenvolva uma API RESTful que permita:
Clientes

    Criar, visualizar, editar e remover clientes.
    Dados obrigatórios: nome e e-mail.
    Um mesmo e-mail não pode se repetir no cadastro.

Favoritos

    Um cliente deve ter uma lista de produtos favoritos.
    Os produtos devem ser validados via API externa (link fornecido abaixo).
    Um produto não pode ser duplicado na lista de um cliente.
    Produtos favoritos devem exibir: ID, título, imagem, preço e review (se houver).
"""


async def get_product_data(product_id: int) -> dict[str, Any]:
    httpx_client = httpx.AsyncClient()
    req = httpx_client.build_request(
        "GET", f"https://fakestoreapi.com/products/{product_id}"
    )
    resp = await httpx_client.send(req)
    if resp.content == b'':
        return {}
    return resp.raise_for_status().json()


@app.post("/client/")
async def create_client(client: ClientBase, session: Session = Depends(get_session)):
    db_client = Client.model_validate(client)
    session.add(db_client)
    # FIXME: There must be a better way to do this
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(500, detail="Integrity Error")
    session.refresh(db_client)
    return db_client


@app.get("/client/{client_id}", response_model=ClientWithFavorites)
async def read_client(client_id: str, session: Session = Depends(get_session)):
    client = session.get(Client, UUID(client_id))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return_favorites = []

    for favorite in client.favorites:
        data = await get_product_data(favorite.product_id)

        data.pop("id")
        data["product_id"] = favorite.product_id
        return_favorites.append(FavoritePublic(**data))

    return_client = ClientWithFavorites(**client.model_dump())
    return_client.favorites = return_favorites

    return return_client


@app.delete("/client/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_client(client_id: str, session: Session = Depends(get_session)):
    client = session.get(Client, UUID(client_id))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    session.delete(client)
    session.commit()


@app.patch("/client/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_client(
    client_id: str, client: Client, session: Session = Depends(get_session)
):
    db_client = session.get(Client, UUID(client_id))
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    client_data = client.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)


@app.get("/client/", response_model=list[ClientWithFavorites])
async def read_clients(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    clients = session.exec(select(Client).offset(offset).limit(limit)).all()

    # FIXME: There must be a better way to do everything here but this works
    return_clients = []

    for client in clients:
        return_favorites = []
        for favorite in client.favorites:
            data = await get_product_data(favorite.product_id)

            data.pop("id")
            data["product_id"] = favorite.product_id
            return_favorites.append(FavoritePublic(**data))

        client_data = ClientWithFavorites(**client.model_dump())
        client_data.favorites = return_favorites
        return_clients.append(client_data)

    return return_clients


@app.post("/favorite/")
async def create_favorite(
    favorite: FavoriteCreate, session: Session = Depends(get_session)
):
    async def validate_product(product_id):
        # FIXME: Get the client from a central location so we can use pool of connections

        data = await get_product_data(product_id)

        return data.get("id", None) is not None

    if not await validate_product(favorite.product_id):
        raise HTTPException(
            status_code=404, detail="Product with id {product_id} does not exist"
        )

    # TODO: This must be the authenticated client
    print("Using the first client we can find")
    client = session.exec(select(Client)).first()

    db_favorite = Favorite.model_validate(favorite)
    db_favorite.client_id = client.id
    db_favorite.product_id = favorite.product_id

    session.add(db_favorite)
    session.commit()
    session.refresh(db_favorite)


@app.delete("/favorite/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(product_id: int, session: Session = Depends(get_session)):
    favorite = session.exec(
        select(Favorite).where(Favorite.product_id == product_id)
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    session.delete(favorite)
    session.commit()
