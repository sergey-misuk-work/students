from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Student
from random import randint


def insert_student(db: Session, student: Student):
    while True:
        try:
            student_id = randint(10000000, 99999999)
            student.id = student_id
            db.add(student)
            db.flush()
            db.commit()
            break
        except IntegrityError:
            pass
