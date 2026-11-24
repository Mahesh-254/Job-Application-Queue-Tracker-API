from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application & Queue Tracker API")

@app.get("/health")
def health_check():
    return {"status": "ok", "day": 5, "database": "connected"}

@app.post("/applications", response_model=schemas.ApplicationResponse, status_code=201)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    db_app = models.Application(**application.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/applications", response_model=List[schemas.ApplicationResponse])
def list_applications(
    client_name: Optional[str] = None,
    role_title: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Application)
    if client_name:
        query = query.filter(models.Application.client_name.ilike(f"%{client_name}%"))
    if role_title:
        query = query.filter(models.Application.role_title.ilike(f"%{role_title}%"))
    if status:
        query = query.filter(models.Application.status == status)
    return query.offset(skip).limit(limit).all()

@app.get("/applications/stats/summary")
def get_application_stats(db: Session = Depends(get_db)):
    total = db.query(models.Application).count()
    by_status = (
        db.query(models.Application.status, func.count(models.Application.id))
        .group_by(models.Application.status)
        .all()
    )
    return {
        "total_applications": total,
        "status_breakdown": {status: count for status, count in by_status},
    }

@app.get("/applications/{app_id}", response_model=schemas.ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app

@app.patch("/applications/{app_id}", response_model=schemas.ApplicationResponse)
def update_application(app_id: int, updates: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/applications/{app_id}", status_code=204)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_app)
    db.commit()
    return None