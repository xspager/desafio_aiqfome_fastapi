from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, Query
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

@app.get("/products/", response_model=List[Product])
async def read_products(session: Session = Depends(get_session), offset: int = 0, limit: int = Query(default=100, le=100)):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products
