from sqlalchemy.orm import Session, joinedload
from app.models.analysis_result_model import AnalysisResult
from app.models.eazybi_config_model import EazyBIReportConfig
from app.models.eazybi_report_model import EazyBIReport
from app.models.models import Report
from app.schemas import AnalysisResultCreate, AnalysisResultUpdate, EazyBIReportConfigCreate, EazyBIReportConfigUpdate, EazyBIReportCreate, ReportCreate, ReportUpdate

def get_analysis_result(db: Session, report_id: str, week: int, year: int, language: str, model: str):
    return db.query(AnalysisResult).options(joinedload(AnalysisResult.eazybi_report)).filter(
        AnalysisResult.report_id == report_id,
        AnalysisResult.week == week,
        AnalysisResult.year == year,
        AnalysisResult.language == language,
        AnalysisResult.model == model
    ).first()

def get_analysis_results(db: Session, week: int, year: int, language: str, model: str):
    return db.query(AnalysisResult).options(joinedload(AnalysisResult.eazybi_report)).filter(
        AnalysisResult.week == week,
        AnalysisResult.year == year,
        AnalysisResult.language == language,
        AnalysisResult.model == model
    ).all()

def create_analysis_result(db: Session, analysis_result: AnalysisResultCreate):
    db_analysis_result = AnalysisResult(**analysis_result.model_dump())
    db.add(db_analysis_result)
    db.commit()
    db.refresh(db_analysis_result)
    return db_analysis_result

def update_analysis_result(db: Session, db_analysis_result: AnalysisResult, analysis_result: AnalysisResultUpdate):
    update_data = analysis_result.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_analysis_result, key, value)
    db.add(db_analysis_result)
    db.commit()
    db.refresh(db_analysis_result)
    return db_analysis_result

def get_eazybi_report_config(db: Session, report_id: str):
    return db.query(EazyBIReportConfig).filter(EazyBIReportConfig.report_id == report_id).first()

def get_eazybi_report_configs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EazyBIReportConfig).offset(skip).limit(limit).all()

def create_eazybi_report_config(db: Session, config: EazyBIReportConfigCreate):
    db_config = EazyBIReportConfig(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def create_eazybi_report(db: Session, eazybi_report: EazyBIReportCreate):
    db_eazybi_report = EazyBIReport(**eazybi_report.model_dump())
    db.add(db_eazybi_report)
    db.commit()
    db.refresh(db_eazybi_report)
    return db_eazybi_report

def update_eazybi_report_config(db: Session, db_config: EazyBIReportConfig, config: EazyBIReportConfigUpdate):
    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_config, key, value)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_eazybi_report_config(db: Session, report_id: str):
    db_config = db.query(EazyBIReportConfig).filter(EazyBIReportConfig.report_id == report_id).first()
    if db_config:
        db.delete(db_config)
        db.commit()
    return db_config

def get_report_by_week_year(db: Session, week: int, year: int):
    return db.query(Report).filter(
        Report.week == week,
        Report.year == year
    ).first()

def create_report(db: Session, report: ReportCreate):
    db_report = Report(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def update_report(db: Session, db_report: Report, report: ReportUpdate):
    update_data = report.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_report, key, value)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report