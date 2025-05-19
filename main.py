from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import Product

def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/products")
async def products_get(*, session, offset, limit):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products
