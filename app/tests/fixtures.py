import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

from sqlmodel import SQLModel, Session, StaticPool, create_engine

from app.main import get_session, app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
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


@pytest.fixture
async def mock_get_product_data():
    with patch("app.main.get_product_data") as mock:
        yield mock
