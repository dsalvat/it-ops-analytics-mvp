from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, List

from app import crud, schemas
from app.core.database import get_db
from app.models.analysis_result_model import AnalysisResult

router = APIRouter()

@router.get("/analysis/all/", response_model=List[schemas.AnalysisResult])
def read_analysis_results(
    week: int,
    year: int,
    language: str,
    model: str,
    db: Session = Depends(get_db),
) -> Any:
    analysis_results = crud.get_analysis_results(db=db, week=week, year=year, language=language, model=model)
    return analysis_results

@router.post("/analysis/", response_model=schemas.AnalysisResult)
def create_or_update_analysis_result(
    *,
    db: Session = Depends(get_db),
    analysis_in: schemas.AnalysisResultCreate,
) -> Any:
    analysis_result = crud.get_analysis_result(db=db, report_id=analysis_in.report_id, week=analysis_in.week, year=analysis_in.year, language=analysis_in.language, model=analysis_in.model)
    if analysis_result:
        analysis_result = crud.update_analysis_result(db=db, db_analysis_result=analysis_result, analysis_result=analysis_in)
    else:
        analysis_result = crud.create_analysis_result(db=db, analysis_result=analysis_in)
    return analysis_result