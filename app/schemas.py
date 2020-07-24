from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime]
    school_grade: Optional[int]
    students_average: Optional[int]


class StudentCreate(StudentBase):
    pass


class StudentRetrieve(StudentBase):
    id: int
    created_at: datetime

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
