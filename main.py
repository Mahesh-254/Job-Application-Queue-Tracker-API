from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application & Queue Tracker API")

@app.get("/health")
def health_check():
    return {"status": "ok", "day": 7, "database": "connected"}

@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = models.User(
        username=user.username,
        hashed_password=auth.hash_password(user.password),
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/applications", response_model=schemas.ApplicationResponse, status_code=201)
def create_application(
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    existing = (
        db.query(models.Application)
        .filter(
            func.lower(models.Application.client_name) == application.client_name.lower(),
            func.lower(models.Application.company_name) == application.company_name.lower(),
            func.lower(models.Application.role_title) == application.role_title.lower(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Duplicate application: client already applied for this role at this company",
        )

    db_app = models.Application(**application.model_dump())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/applications", response_model=List[schemas.ApplicationResponse])
def list_applications(
    client_name: Optional[str] = None,
    role_title: Optional[str] = None,
    status: Optional[schemas.ApplicationStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Application)
    if client_name:
        query = query.filter(models.Application.client_name.ilike(f"%{client_name}%"))
    if role_title:
        query = query.filter(models.Application.role_title.ilike(f"%{role_title}%"))
    if status:
        query = query.filter(models.Application.status == status.value)
    return query.offset(skip).limit(limit).all()

@app.get("/applications/stats/summary")
def get_application_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
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
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app

@app.patch("/applications/{app_id}", response_model=schemas.ApplicationResponse)
def update_application(
    app_id: int,
    updates: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/applications/{app_id}", status_code=204)
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_app = db.query(models.Application).filter(models.Application.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_app)
    db.commit()
    return None