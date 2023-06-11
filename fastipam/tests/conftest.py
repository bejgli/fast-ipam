import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastipam import crud, schemas
from fastipam.dependencies import get_db
from fastipam.main import api_app
from fastipam.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# conftest.py

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    db = TestingSessionLocal(bind=connection)
    # db = Session(db_engine)

    yield db

    db.rollback()
    connection.close()


# 
@pytest.fixture(scope="function")
def client(db):
    api_app.dependency_overrides[get_db] = lambda: db

    with TestClient(api_app) as c: # úgy néz ki a dependency override esetében nem elég a fő appot használni
        yield c

#@pytest.fixture
#def subnets(db):
#    crud.create_subnet(db, schemas.SubnetCreate(name="test", ))
#    create_item(db, schemas.ItemCreate(title="item 2"))