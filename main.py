from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application & Queue Tracker API")

@app.get("/health")
def health_check():
    return {"status": "ok", "day": 3, "database": "connected"}

@app.post("/applications", response_model=schemas.ApplicationResponse, status_code=201)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    db_app = models.Application(**application.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/applications", response_model=List[schemas.ApplicationResponse])
def list_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Application).offset(skip).limit(limit).all()