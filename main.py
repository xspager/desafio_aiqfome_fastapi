from uuid import UUID

from contextlib import asynccontextmanager
from typing import List

from sqlalchemy.exc import IntegrityError

from fastapi import Depends, FastAPI, Query, HTTPException, status
from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import ClientCreate, Product, Client


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


@app.get("/product/", response_model=List[Product])
async def read_products(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products


@app.post("/client/")
async def create_client(client: ClientCreate, session: Session = Depends(get_session)):
    db_client = Client.model_validate(client)
    session.add(db_client)
    # FIXME: There must be a better way to do this
    try:
        session.commit()
    except IntegrityError as e:
        raise HTTPException(500, detail="Integrity Error")
    session.refresh(db_client)
    return db_client


@app.delete("/client/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_client(client_id: str, session: Session = Depends(get_session)):
    client = session.get(Client, UUID(client_id))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")


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


@app.get("/client/", response_model=list[Client])
async def read_clients(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    clients = session.exec(select(Client).offset(offset).limit(limit)).all()
    return clients
