from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import models
from auth import get_password_hash
import pytest
from datetime import date
from utils import insert_student
import operator


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
        models.User(username="test", hashedPassword=get_password_hash("test"))
    )
    test_db.flush()
    test_db.commit()
    return


@pytest.fixture
def test_students(test_db):
    test_db.query(models.Student).delete()
    test_db.flush()
    test_db.commit()

    insert_student(
        test_db,
        models.Student(
            firstName="Cynthia",
            lastName="Henderson",
            dateOfBirth=date(2000, 1, 2),
            schoolGrade=6,
            average=60,
        ),
    )
    insert_student(
        test_db,
        models.Student(
            firstName="Marilyn",
            lastName="Snyder",
            dateOfBirth=date(2001, 2, 3),
            schoolGrade=8,
            average=70,
        ),
    )
    insert_student(
        test_db,
        models.Student(
            firstName="David",
            lastName="Dandrea",
            dateOfBirth=date(2002, 3, 4),
            schoolGrade=8,
            average=80,
        ),
    )
    return test_db.query(models.Student).all()


@pytest.fixture(scope="module")
def test_token(test_user):
    response = client.post("/token", data={"username": "test", "password": "test"})
    return response.json()["access_token"]


def test_create_token(test_user):
    response = client.post("/token", data={"username": "test", "password": "test"})

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert len(body["access_token"])

    assert "token_type" in body
    assert body["token_type"] == "bearer"


def test_protected_routes():
    pass


def test_retrieve_students(test_students, test_token):
    response = client.get(
        "/students", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "totalStudents" in body
    assert body["totalStudents"] == 3

    assert "students" in body
    for student in body["students"]:
        assert len(str(student["id"])) == 8

    # check ordering
    response = client.get(
        "/students?order_by=last_name",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    body = response.json()

    assert "totalStudents" in body
    assert body["totalStudents"] == 3
    assert "students" in body
    assert tuple(map(operator.itemgetter("lastName"), body["students"])) == (
        "Dandrea",
        "Henderson",
        "Snyder",
    )

    response = client.get(
        "/students?order_by=age", headers={"Authorization": f"Bearer {test_token}"},
    )

    body = response.json()

    assert "totalStudents" in body
    assert body["totalStudents"] == 3
    assert "students" in body
    # dates are pretty complicated to be verified, so we check name order
    assert tuple(map(operator.itemgetter("firstName"), body["students"])) == (
        "David",
        "Marilyn",
        "Cynthia",
    )

    response = client.get(
        "/students?order_by=grade", headers={"Authorization": f"Bearer {test_token}"},
    )

    body = response.json()

    assert "totalStudents" in body
    assert body["totalStudents"] == 3
    assert "students" in body
    assert tuple(map(operator.itemgetter("schoolGrade"), body["students"])) == (8, 8, 6)


def test_create_student(test_students, test_token, test_db):
    student_json = {
        "firstName": "John",
        "lastName": "Doe",
        "dateOfBirth": "2003-04-05T00:00:00.000Z",
        "schoolGrade": 5,
        "average": 55,
    }
    response = client.post(
        "/students",
        headers={"Authorization": f"Bearer {test_token}"},
        json=student_json,
    )

    assert response.status_code == 200

    body = response.json()

    assert "id" in body
    assert len(str(body["id"])) == 8

    assert "createdAt" in body

    assert test_db.query(models.Student).count() == 4

    # check validation
    student_json["schoolGrade"] = 13
    student_json["average"] = 101

    response = client.post(
        "/students",
        headers={"Authorization": f"Bearer {test_token}"},
        json=student_json,
    )

    assert response.status_code == 422

    body = response.json()

    assert "detail" in body

    error_location = body["detail"][0]["loc"]
    assert error_location == ["body", "student", "schoolGrade"]

    error_location = body["detail"][1]["loc"]
    assert error_location == ["body", "student", "average"]


def test_delete_student(test_students, test_token, test_db):
    response = client.post(
        "/students",
        headers={"Authorization": f"Bearer {test_token}"},
        json={
            "firstName": "John",
            "lastName": "Doe",
            "dateOfBirth": "2003-04-05T00:00:00.000Z",
            "schoolGrade": 5,
            "average": 55,
        },
    )

    assert test_db.query(models.Student).count() == 4

    body = response.json()
    student_id = body["id"]

    response = client.delete(
        f"/students/{student_id}", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "deletedAt" in body

    assert test_db.query(models.Student).count() == 3


def test_get_average_for_grade(test_students, test_token):
    response = client.get(
        "/stat/grade/6", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "grade" in body
    assert body["grade"] == 6
    assert "average" in body
    assert body["average"] == 60
    assert "numStudents" in body
    assert body["numStudents"] == 1

    response = client.get(
        "/stat/grade/8", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "grade" in body
    assert body["grade"] == 8
    assert "average" in body
    assert body["average"] == 75
    assert "numStudents" in body
    assert body["numStudents"] == 2


def test_std_dev_for_grade(test_students, test_token):
    response = client.get(
        "/stat/std-dev/6", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "grade" in body
    assert body["grade"] == 6
    assert "average" in body
    assert body["average"] == 60.0
    assert "stdDev" in body
    assert body["stdDev"] == 0
    assert "numStudents" in body
    assert body["numStudents"] == 1

    response = client.get(
        "/stat/std-dev/8", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "grade" in body
    assert body["grade"] == 8
    assert "average" in body
    assert body["average"] == 75.0
    assert "stdDev" in body
    assert body["stdDev"] == 5.0
    assert "numStudents" in body
    assert body["numStudents"] == 2


def test_delete_all_students(test_students, test_token, test_db):
    response = client.delete(
        "/students", headers={"Authorization": f"Bearer {test_token}"}
    )

    assert response.status_code == 200

    body = response.json()

    assert "numStudents" in body
    assert body["numStudents"] == 0
    assert test_db.query(models.Student).count() == 0
