from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    # TODO: handle time zone
    date_of_birth = Column(DateTime(timezone=True), server_default=func.now())
    school_grade = Column(Integer)
    students_average = Column(Integer)
