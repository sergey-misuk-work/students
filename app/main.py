from fastapi import FastAPI, Depends
from database import SessionLocal, engine
import models, schemas
from sqlalchemy.orm import Session
from typing import List


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/students", response_model=List[schemas.StudentRetrieveResponse])
async def students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()
