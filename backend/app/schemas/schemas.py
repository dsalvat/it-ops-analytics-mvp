from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DataSourceType(str, Enum):
    EAZYBI = "eazybi"
    JIRA = "jira"
    MONITORING = "monitoring"

class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"

# Data Sources
class DataSourceBase(BaseModel):
    name: str
    type: DataSourceType
    api_config: Optional[Dict[str, Any]] = None

class DataSourceCreate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Extractions
class ExtractionBase(BaseModel):
    extraction_type: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    processed_data: Optional[Dict[str, Any]] = None

class ExtractionCreate(ExtractionBase):
    source_id: int

class Extraction(ExtractionBase):
    id: int
    source_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# AI Analysis
class AIAnalysisBase(BaseModel):
    prompt_used: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    analysis_type: Optional[str] = None

class AIAnalysisCreate(AIAnalysisBase):
    extraction_id: int

class AIAnalysis(AIAnalysisBase):
    id: int
    extraction_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# User Insights
class UserInsightBase(BaseModel):
    feedback: str
    priority: Optional[Priority] = None

class UserInsightCreate(UserInsightBase):
    analysis_id: int
    user_id: int

class UserInsight(UserInsightBase):
    id: int
    analysis_id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Reports
class ReportBase(BaseModel):
    week: int
    year: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    report_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    week: int
    year: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReportUpdate(BaseModel):
    week: Optional[int] = None
    year: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    report_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

# Specific schemas for API responses
class SLAOverview(BaseModel):
    total_tickets: int
    p1_within_sla: int
    p1_outside_sla: int
    p2_within_sla: int
    p2_outside_sla: int
    overall_compliance: float

class TicketAnalysis(BaseModel):
    created_this_week: int
    resolved_this_week: int
    pending_tickets: int
    avg_resolution_time: float
    by_priority: Dict[str, int]

class SatisfactionMetrics(BaseModel):
    avg_satisfaction: float
    total_surveys: int
    completion_rate: float
    by_team: Dict[str, float]

class AnalysisRequest(BaseModel):
    data_type: str = Field(..., description="Type of analysis: sla, tickets, satisfaction")
    time_period: Optional[str] = Field(default="last_week", description="Time period for analysis")
    include_recommendations: bool = Field(default=True, description="Include AI recommendations")

# EazyBI Reports
class EazyBIReportBase(BaseModel):
    week: int
    year: int
    report_data: Optional[Dict[str, Any]] = None

class EazyBIReportCreate(EazyBIReportBase):
    pass

class EazyBIReport(EazyBIReportBase):
    id: int
    week: int
    year: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analysis Results
class AnalysisResultBase(BaseModel):
    report_id: str
    week: int
    year: int
    language: str
    model: str
    eazybi_report_id: Optional[int] = None
    llm_response: Optional[Any] = None

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResultUpdate(BaseModel):
    report_id: Optional[str] = None
    week: Optional[int] = None
    year: Optional[int] = None
    language: Optional[str] = None
    model: Optional[str] = None
    eazybi_report_id: Optional[int] = None
    llm_response: Optional[Any] = None

class AnalysisResult(AnalysisResultBase):
    id: int
    created_at: datetime
    updated_at: datetime
    eazybi_report: Optional[EazyBIReport] = None

    class Config:
        from_attributes = True

# EazyBI Report Config
class EazyBIReportConfigBase(BaseModel):
    report_id: str
    name: str
    llm_analysis_call: Optional[str] = None

class EazyBIReportConfigCreate(EazyBIReportConfigBase):
    pass

class EazyBIReportConfigUpdate(EazyBIReportConfigBase):
    pass

class EazyBIReportConfig(EazyBIReportConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True