from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ApplicationCreate(BaseModel):
    client_name: str
    company_name: str
    role_title: str
    status: Optional[str] = "Submitted"

class ApplicationUpdate(BaseModel):
    client_name: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    status: Optional[str] = None

class ApplicationResponse(ApplicationCreate):
    id: int
    applied_at: datetime

    class Config:
        from_attributes = True