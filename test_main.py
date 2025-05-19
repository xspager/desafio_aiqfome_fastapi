import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session
from models import Product, Client


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


def test_products_get(client: TestClient, session: Session):
    product = Product()
    session.add(product)
    session.commit()

    response = client.get("/product/")

    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1


def test_create_client(client: TestClient, session: Session):
    response = client.post(
        "/client/", json={"name": "Bob Tables", "email": "an@email.c"}
    )

    data = response.json()
    assert response.status_code == 200
    assert data["id"] is not None


def test_delete_client(client: TestClient, session: Session):
    c_client = Client(name="Bob Tables", email="another clearly not an email")
    session.add(c_client)
    session.commit()
    session.refresh(c_client)

    response = client.delete(f"/client/{c_client.id}")

    assert response.status_code == 204


def test_edit_client(client: TestClient, session: Session):
    c_client = Client(name="Who's Bob Tables", email="another clearly not an email")
    session.add(c_client)
    session.commit()
    session.refresh(c_client)

    response = client.patch(
        f"/client/{c_client.id}", json={"name": "Totally regular user name"}
    )

    session.refresh(c_client)

    assert response.status_code == 204
    assert c_client.name == "Totally regular user name"


def test_client_email_must_be_unique(client: TestClient, session: Session):
    response = client.post("/client/", json={"name": "Bob", "email": "bob@email.com"})

    assert response.status_code == 200

    # FIXME: Is this the best way?
    with pytest.raises(Exception):
        response = client.post(
            "/client/", json={"name": "Bob2", "email": "bob@email.com"}
        )

        assert response.status_code == 200
