from fastapi import FastAPI, Depends, HTTPException, status
from services.database import engine, get_db
import models
import schemas
from sqlalchemy.orm import Session
from schemas import TokenRetrieve
from fastapi.security import OAuth2PasswordRequestForm
from services.auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
    get_current_user,
)
from datetime import timedelta
from services.students import (
    insert_student,
    get_students,
    get_student,
    delete_student as delete_student_in_db,
    delete_students,
    count_students,
)
from services.calc import calc_average_for_grade, calc_std_dev_for_grade


models.Base.metadata.create_all(bind=engine)

# create a test user
session = next(get_db())
session.merge(models.User(username="test", hashedPassword=get_password_hash("test")))
session.flush()
session.commit()

app = FastAPI()


@app.get("/students", response_model=schemas.StudentRetrieveList)
async def students(
    order_by: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    students = get_students(db, order_by)
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
    student = get_student(db, student_id)
    delete_student_in_db(db, student=student)
    return student


@app.get("/stat/grade/{grade}", response_model=schemas.AverageForGrade)
async def get_average_for_grade(
    grade: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = calc_average_for_grade(db, grade)
    return dict(zip(("grade", "average", "numStudents"), result))


@app.get("/stat/std-dev/{grade}", response_model=schemas.StdDevForGrade)
async def get_std_dev_for_grade(
    grade: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = calc_std_dev_for_grade(db, grade)
    result["grade"] = grade
    return result


@app.delete("/students", response_model=schemas.StudentDeleteAll)
async def delete_all_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    delete_students(db)
    return {"numStudents": count_students(db)}


@app.get("/students/{student_id}", response_model=schemas.StudentRetrieve)
async def retrieve_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_student(db, student_id)


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
