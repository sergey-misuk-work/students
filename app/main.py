from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, get_db
import models
import schemas
from sqlalchemy.orm import Session
from schemas import TokenRetrieve
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
    get_current_user,
)
from datetime import timedelta
from utils import insert_student
from sqlalchemy.sql import func
import operator
import functools


models.Base.metadata.create_all(bind=engine)

# create a test user
session = next(get_db())
session.merge(models.User(username="test", hashed_password=get_password_hash("test")))
session.flush()
session.commit()

app = FastAPI()


@app.get("/students", response_model=schemas.StudentRetrieveList)
async def students(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    students = db.query(models.Student).all()
    return schemas.StudentRetrieveList(students=students, totalStudents=len(students))


@app.post("/students", response_model=schemas.StudentRetrieve)
async def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return insert_student(db, models.Student(**student.dict()))


@app.delete("/students/{student_id}", response_model=schemas.StudentDelete)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter_by(id=student_id).first()
    db.delete(student)
    db.flush()
    db.commit()
    return student


@app.get("/stat/grade/{grade}", response_model=schemas.AverageForGrade)
async def get_average_for_grade(
    grade: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = (
        db.query(
            models.Student.school_grade.label("grade"),
            func.avg(models.Student.students_average).label("average"),
            func.count(models.Student.id).label("numStudents"),
        )
        .filter_by(school_grade=grade)
        .group_by(models.Student.school_grade)
        .first()
    )
    return dict(zip(("grade", "average", "numStudents"), result))


@app.get("/stat/std-dev/{grade}", response_model=schemas.StdDevForGrade)
async def get_std_dev_for_grade(
    grade: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    m, n = (
        db.query(
            func.avg(models.Student.students_average).label("average"),
            func.count(models.Student.id).label("numStudents"),
        )
        .filter_by(school_grade=grade)
        .group_by(models.Student.school_grade)
        .first()
    )
    students_average_values = map(
        operator.itemgetter(0),
        db.query(models.Student.students_average).filter_by(school_grade=grade).all(),
    )
    # TODO: make more readable
    std_dev = pow(
        sum(
            map(
                functools.partial(pow, exp=2),
                map(functools.partial(operator.sub, m), students_average_values),
            )
        )
        / n,
        0.5,
    )

    return {"grade": grade, "average": m, "stdDev": std_dev, "numStudents": n}


@app.post("/token", response_model=TokenRetrieve)
async def create_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
