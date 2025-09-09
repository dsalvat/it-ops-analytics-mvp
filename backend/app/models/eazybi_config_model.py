from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class EazyBIReportConfig(Base):
    __tablename__ = "eazybi_report_configs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    llm_analysis_call = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())