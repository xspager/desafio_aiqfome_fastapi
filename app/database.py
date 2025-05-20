import os

from sqlmodel import SQLModel, create_engine


if os.environ.get("RUNNING_ON_DOCKER_COMPOSE", False):
    user = os.environ.get("POSTGRES_USER", "user")
    password = os.environ.get("POSTGRES_PASSWORD", "password")
    db = os.environ.get("POSTGRES_DB", "db")

    engine = create_engine(f"postgresql+psycopg://{user}:{password}@db/{db}")
else:
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
