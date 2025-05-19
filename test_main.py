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

def test_products_get(session):
    def get_session_override():
          return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    response = client.get("/products")
    app.dependency_overrides.clear()
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Hello, World!"