from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class ApplicationStatus(str, Enum):
    SUBMITTED = "Submitted"
    INTERVIEW = "Interview"
    REJECTED = "Rejected"
    OFFER = "Offer"

class ApplicationCreate(BaseModel):
    client_name: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)
    role_title: str = Field(..., min_length=1)
    status: ApplicationStatus = ApplicationStatus.SUBMITTED

    @field_validator("client_name", "company_name", "role_title")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank")
        return cleaned

class ApplicationUpdate(BaseModel):
    client_name: Optional[str] = None
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class ApplicationResponse(BaseModel):
    id: int
    client_name: str
    company_name: str
    role_title: str
    status: ApplicationStatus
    applied_at: datetime

    class Config:
        from_attributes = True