import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session
from models import Product

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client    
    app.dependency_overrides.clear()


def test_products_get(client: TestClient, session: Session):
    product = Product()
    session.add(product)
    session.commit()

    response = client.get("/products/")
    
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1