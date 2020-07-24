from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import models
from auth import get_password_hash
import pytest
from datetime import date


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    yield from override_get_db()


@pytest.fixture(scope="module")
def test_user(test_db):
    test_db.merge(
        models.User(username="test", hashed_password=get_password_hash("test"))
    )
    test_db.flush()
    test_db.commit()
    return


@pytest.fixture
def test_students(test_db):
    test_db.query(models.Student).delete()
    test_db.add(
        models.Student(
            first_name="Cynthia",
            last_name="Henderson",
            date_of_birth=date(2000, 1, 2),
            school_grade=6,
            students_average=60,
        )
    )
    test_db.add(
        models.Student(
            first_name="Marilyn",
            last_name="Snyder",
            date_of_birth=date(2001, 2, 3),
            school_grade=8,
            students_average=70,
        )
    )
    test_db.add(
        models.Student(
            first_name="David",
            last_name="Dandrea",
            date_of_birth=date(2002, 3, 4),
            school_grade=10,
            students_average=80,
        )
    )
    test_db.flush()
    test_db.commit()
    return test_db.query(models.Student).all()


def test_create_token(test_user):
    response = client.post("/token", data={"username": "test", "password": "test"})

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert len(body["access_token"])

    assert "token_type" in body
    assert body["token_type"] == "bearer"


def test_retrieve_students(test_students):
    response = client.get("/students")

    assert response.status_code == 200
    body = response.json()
    assert "totalStudents" in body
    assert body["totalStudents"] == 3
