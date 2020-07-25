from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class StudentBase(BaseModel):
    firstName: str
    lastName: str
    dateOfBirth: Optional[datetime]
    schoolGrade: Optional[int]
    average: Optional[int]


class StudentCreate(StudentBase):
    @validator("schoolGrade")
    def check_school_grade(cls, value):
        if 1 <= value <= 12:
            return value
        raise ValueError("School grade takes values between 1 and 12")

    @validator("average")
    def check_students_average(cls, value):
        if 0 <= value <= 100:
            return value
        raise ValueError("Student's average takes values between 0 and 100")


class StudentRetrieve(StudentBase):
    id: int
    createdAt: datetime

    class Config:
        orm_mode = True


class StudentDelete(StudentBase):
    deletedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class StudentRetrieveList(BaseModel):
    totalStudents: int
    students: List[StudentRetrieve]


class TokenRetrieve(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AverageForGrade(BaseModel):
    grade: int
    average: int
    numStudents: int


class StdDevForGrade(BaseModel):
    grade: int
    average: float
    stdDev: float
    numStudents: int


class StudentDeleteAll(BaseModel):
    numStudents: int
