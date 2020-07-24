from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime]
    school_grade: Optional[int]
    students_average: Optional[int]


class StudentCreateRequest(StudentBase):
    pass


class StudentRetrieveResponse(StudentBase):
    id: int

    class Config:
        orm_mode = True


class TokenRetrieve(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserRetrieve(BaseModel):
    username: str


class UserInternal(UserRetrieve):
    hashed_password: str
