from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True, nullable=False)
    company_name = Column(String, index=True, nullable=False)
    role_title = Column(String, index=True, nullable=False)
    status = Column(String, default="Submitted")  # Submitted, Interview, Rejected, Offer
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="applier")  # applier or reviewer