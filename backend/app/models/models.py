from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.types import DECIMAL as Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class DataSourceType(str, enum.Enum):
    EAZYBI = "eazybi"
    JIRA = "jira"
    MONITORING = "monitoring"

class DataSourceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Priority(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(DataSourceType), nullable=False)
    api_config = Column(JSON)
    status = Column(Enum(DataSourceStatus), default=DataSourceStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    extractions = relationship("Extraction", back_populates="source")

class Extraction(Base):
    __tablename__ = "extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    raw_data = Column(JSON)
    processed_data = Column(JSON)
    extraction_type = Column(String(100))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    source = relationship("DataSource", back_populates="extractions")
    analysis = relationship("AIAnalysis", back_populates="extraction")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    extraction_id = Column(Integer, ForeignKey("extractions.id"))
    prompt_used = Column(Text)
    result = Column(JSON)
    confidence = Column(Decimal(3, 2))
    analysis_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    extraction = relationship("Extraction", back_populates="analysis")
    user_insights = relationship("UserInsight", back_populates="analysis")

class UserInsight(Base):
    __tablename__ = "user_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("ai_analysis.id"))
    user_id = Column(Integer)  # Will be FK to users table when implemented
    feedback = Column(Text)
    priority = Column(Enum(Priority))
    status = Column(Enum("pending", "approved", "rejected", name="insight_status"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("AIAnalysis", back_populates="user_insights")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    report_data = Column(JSON)
    recommendations = Column(JSON)
    status = Column(Enum("draft", "final", "sent", name="report_status"), default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
