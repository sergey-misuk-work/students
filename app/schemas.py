from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime]
    school_grade: Optional[int]
    students_average: Optional[int]


class StudentCreate(StudentBase):
    @validator("school_grade")
    def check_school_grade(cls, value):
        if 1 <= value <= 12:
            return value
        raise ValueError("School grade takes values between 1 and 12")

    @validator("students_average")
    def check_students_average(cls, value):
        if 0 <= value <= 100:
            return value
        raise ValueError("Student's average takes values between 0 and 100")


class StudentRetrieve(StudentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class StudentDelete(StudentBase):
    deleted_at: datetime = Field(default_factory=datetime.now)

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
