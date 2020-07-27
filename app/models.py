from sqlalchemy import Column, Integer, String, DateTime
from services.database import Base
from sqlalchemy.sql import func


class Student(Base):
    __tablename__ = "students"

    studentId = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    # TODO: handle time zone
    dateOfBirth = Column(DateTime(timezone=True))
    schoolGrade = Column(Integer)
    average = Column(Integer)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashedPassword = Column(String, nullable=False)
