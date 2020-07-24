from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from sqlalchemy.sql import func


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    # TODO: handle time zone
    date_of_birth = Column(DateTime(timezone=True))
    school_grade = Column(Integer)
    students_average = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
