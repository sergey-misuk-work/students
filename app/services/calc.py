from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Student
import operator
import functools


def calc_average_for_grade(db: Session, grade: int):
    return (
        db.query(
            Student.schoolGrade.label("grade"),
            func.avg(Student.average).label("average"),
            func.count(Student.studentId).label("numStudents"),
        )
        .filter_by(schoolGrade=grade)
        .group_by(Student.schoolGrade)
        .first()
    )


def calc_std_dev_for_grade(db: Session, grade: int):
    m, n = (
        db.query(
            func.avg(Student.average).label("average"),
            func.count(Student.studentId).label("numStudents"),
        )
        .filter_by(schoolGrade=grade)
        .group_by(Student.schoolGrade)
        .first()
    )
    average_values = map(
        operator.itemgetter(0),
        db.query(Student.average).filter_by(schoolGrade=grade).all(),
    )
    # TODO: make more readable
    std_dev = pow(
        sum(
            map(
                functools.partial(pow, exp=2),
                map(functools.partial(operator.sub, m), average_values),
            )
        )
        / n,
        0.5,
    )

    return {"average": m, "stdDev": std_dev, "numStudents": n}
