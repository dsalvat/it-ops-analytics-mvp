from sqlalchemy import Column, Integer, JSON, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base

class EazyBIReport(Base):
    __tablename__ = "eazybi_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, index=True) # Added report_id
    week = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    report_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
