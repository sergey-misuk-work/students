from fastapi import FastAPI, Depends, HTTPException, status
from database import engine, get_db
import models
import schemas
from sqlalchemy.orm import Session
from typing import List
from schemas import TokenRetrieve
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
)
from datetime import timedelta


models.Base.metadata.create_all(bind=engine)

# create a test user
session = next(get_db())
session.merge(models.User(username="test", hashed_password=get_password_hash("test")))
session.flush()
session.commit()

app = FastAPI()


@app.get("/students", response_model=List[schemas.StudentRetrieveResponse])
async def students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.post("/token", response_model=TokenRetrieve)
async def create_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
