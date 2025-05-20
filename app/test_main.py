import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app, get_session
from app.models import Client, Favorite


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


def test_create_client(client: TestClient, session: Session):
    response = client.post(
        "/client/", json={"name": "Bob Tables", "email": "an@email.c"}
    )

    data = response.json()
    assert response.status_code == 200
    assert data["id"] is not None


def test_read_client(client: TestClient, session: Session):
    c_client = Client(name="Bob Tables", email="another clearly not an email")
    session.add(c_client)
    session.commit()
    session.refresh(c_client)

    response = client.get(f"/client/{c_client.id}")

    assert response.status_code == 200


def test_delete_client(client: TestClient, session: Session):
    c_client = Client(name="Bob Tables", email="another clearly not an email")
    session.add(c_client)
    session.commit()
    session.refresh(c_client)

    response = client.delete(f"/client/{c_client.id}")

    assert response.status_code == 204
    assert session.get(Client, c_client.id) is None


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


def test_edit_client_with_same_email(client: TestClient, session: Session):
    client_a = Client(name="Who's Bob Tables", email="another clearly not an email")
    client_b = Client(name="Who's Who", email="not an email")
    session.add_all([client_a, client_b])
    session.commit()
    session.refresh(client_b)

    with pytest.raises(Exception):
        client.patch(
            f"/client/{client_b.id}", json={"email": "another clearly not an email"}
        )


def test_client_email_must_be_unique(client: TestClient, session: Session):
    response = client.post("/client/", json={"name": "Bob", "email": "bob@email.com"})
    assert response.status_code == 200

    response = client.post("/client/", json={"name": "Bob2", "email": "bob@email.com"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Integrity Error"}


def test_get_all_clients(client: TestClient, session: Session):
    client_a = Client(name="Bob Tables", email="bob@table.com")
    client_b = Client(name="Bob Tables", email="other_bob@table.com")
    session.add_all([client_a, client_b])
    session.commit()

    response = client.get("/client/")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


# TODO: Mock requests to external API


@pytest.mark.asyncio
def test_create_favorite(client: TestClient, session: Session):
    c_client = Client(name="My favorite Client", email="another clearly not an email")
    session.add(c_client)
    session.commit()

    response = client.post(
        "/favorite/",
        json={
            "product_id": 1,
        },
    )

    assert response.status_code == 200
    session.refresh(c_client)
    assert len(c_client.favorites) == 1


@pytest.mark.asyncio
def test_create_duplicate_favorite(client: TestClient, session: Session):
    c_client = Client(name="My favorite Client", email="another clearly not an email")
    favorite = Favorite(product_id=1, client=c_client)
    session.add(c_client)
    session.add(favorite)
    session.commit()

    with pytest.raises(Exception):
        client.post(
            "/favorite/",
            json={
                "product_id": 1,
            },
        )


@pytest.mark.asyncio
def test_delete_favorite(client: TestClient, session: Session):
    c_client = Client(name="My favorite Client", email="another clearly not an email")
    favorite = Favorite(product_id=1, client=c_client)
    session.add(c_client)
    session.add(favorite)
    session.commit()

    session.refresh(c_client)
    assert len(c_client.favorites) == 1

    response = client.delete(
        "/favorite/1",
    )

    session.refresh(c_client)

    assert response.status_code == 204
    assert len(c_client.favorites) == 0
