from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Student
from random import randint


def insert_student(db: Session, student: Student):
    while True:
        try:
            student_id = randint(10000000, 99999999)
            student.studentId = student_id
            db.add(student)
            db.flush()
            db.commit()
            return student
        except IntegrityError:
            pass


def get_students(db: Session, order_by: str = None):
    students = db.query(Student)
    if order_by:
        if order_by in {"last_name", "age", "grade"}:
            if order_by == "last_name":
                students = students.order_by(Student.lastName.asc())
            elif order_by == "age":
                students = students.order_by(Student.dateOfBirth.desc())
            elif order_by == "grade":
                students = students.order_by(Student.schoolGrade.desc())
    return students.all()


def get_student(db: Session, student_id: int):
    return db.query(Student).filter_by(studentId=student_id).first()


def delete_student(db: Session, student_id: int = -1, student: Student = None):
    if student_id > 0:
        raise NotImplementedError("For now deletion by id is not supported yet")
    elif not student:
        raise ValueError("Student object is required")
    db.delete(student)
    db.flush()
    db.commit()


def delete_students(db: Session):
    db.query(Student).delete()
    db.flush()
    db.commit()


def count_students(db):
    return db.query(Student).count()
