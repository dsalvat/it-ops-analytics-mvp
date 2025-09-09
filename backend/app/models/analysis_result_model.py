from sqlalchemy import Column, Integer, String, JSON, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.eazybi_report_model import EazyBIReport

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), nullable=False)
    week = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    language = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    eazybi_report_id = Column(Integer, ForeignKey("eazybi_reports.id"))
    llm_response = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('report_id', 'week', 'year', 'language', 'model', name='_report_week_year_language_model_uc'),)
    
    eazybi_report = relationship("EazyBIReport")