from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import httpx
import base64
import json
from datetime import datetime
import logging

from app.core.config import settings
from app.core.database import get_db
from app import crud, schemas
from app.models.eazybi_config_model import EazyBIReportConfig

router = APIRouter()

@router.get("/config", response_model=List[schemas.EazyBIReportConfig])
async def get_eazybi_config(db: Session = Depends(get_db)):
    """
    Retrieve Eazybi report configurations from the database.
    """
    configs = crud.get_eazybi_report_configs(db)
    if not configs:
        try:
            with open("/app/app/core/eazybi_config.json", "r") as f:
                eazybi_reports_config_from_file = json.load(f)
            
            logging.info(f"Found {len(eazybi_reports_config_from_file)} configs in eazybi_config.json")
            for config_data in eazybi_reports_config_from_file:
                config_data["report_id"] = str(config_data["report_id"])
                config_in = schemas.EazyBIReportConfigCreate(**config_data)
                crud.create_eazybi_report_config(db, config_in)
                logging.info(f"Created config for report_id: {config_data['report_id']}")
            configs = crud.get_eazybi_report_configs(db)
            logging.info(f"After population, found {len(configs)} configs in DB.")
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Eazybi configuration file not found and no configs in DB."
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error decoding Eazybi configuration file."
            )
    return configs

@router.post("/config", response_model=schemas.EazyBIReportConfig)
async def create_eazybi_config(config: schemas.EazyBIReportConfigCreate, db: Session = Depends(get_db)):
    db_config = crud.get_eazybi_report_config(db, report_id=config.report_id)
    if db_config:
        raise HTTPException(status_code=400, detail="Report config with this ID already exists")
    return crud.create_eazybi_report_config(db, config)

@router.put("/config/{report_id}", response_model=schemas.EazyBIReportConfig)
async def update_eazybi_config(report_id: str, config: schemas.EazyBIReportConfigUpdate, db: Session = Depends(get_db)):
    db_config = crud.get_eazybi_report_config(db, report_id=report_id)
    if not db_config:
        raise HTTPException(status_code=404, detail="Report config not found")
    return crud.update_eazybi_report_config(db, db_config, config)

@router.delete("/config/{report_id}", response_model=schemas.EazyBIReportConfig)
async def delete_eazybi_config(report_id: str, db: Session = Depends(get_db)):
    db_config = crud.delete_eazybi_report_config(db, report_id=report_id)
    if not db_config:
        raise HTTPException(status_code=404, detail="Report config not found")
    return db_config

@router.get("/eazybi-data")
async def get_eazybi_data(db: Session = Depends(get_db), week: int = None, year: int = None):
    username = settings.EAZYBI_USERNAME
    password = settings.EAZYBI_PASSWORD

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eazybi credentials not configured."
        )

    auth_string = f"{username}:{password}"
    encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_auth_string}"}

    eazybi_reports_config = crud.get_eazybi_report_configs(db)
    if not eazybi_reports_config:
        # Add logic to populate from file if empty, similar to get_eazybi_config
        try:
            with open("/app/app/core/eazybi_config.json", "r") as f:
                eazybi_reports_config_from_file = json.load(f)
            
            for config_data in eazybi_reports_config_from_file:
                config_data["report_id"] = str(config_data["report_id"])
                config_in = schemas.EazyBIReportConfigCreate(**config_data)
                crud.create_eazybi_report_config(db, config_in)
            eazybi_reports_config = crud.get_eazybi_report_configs(db) # Re-fetch after populating
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Eazybi configuration file not found and no configs in DB."
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error decoding Eazybi configuration file."
            )
        # If still no configs after trying to populate, then raise 404
        if not eazybi_reports_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Eazybi report configurations found after attempting to load from file."
            )

    if week is None or year is None:
        week = datetime.now().isocalendar()[1]
        year = datetime.now().year
        
    all_results = []

    async with httpx.AsyncClient() as client:
        for report_config in eazybi_reports_config:
            report_id = report_config.report_id
            
            existing_report = crud.get_analysis_result(
                db,
                report_id=report_id,
                week=week,
                year=year,
                language='eazybi',
                model='eazybi'
            )

            if existing_report:
                all_results.append({"report_name": report_config.name, "status": "Already processed"})
                continue

            eazybi_url = f"{settings.EAZYBI_BASE_URL}/{report_id}.json"
            try:
                response = await client.get(eazybi_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "query_results" in data:
                    report_data = data["query_results"]
                    
                    eazybi_report_create = schemas.EazyBIReportCreate(week=week, year=year, report_data=report_data)
                    eazybi_report = crud.create_eazybi_report(db, eazybi_report_create)

                    analysis_result = schemas.AnalysisResultCreate(
                        report_id=report_id,
                        week=week,
                        year=year,
                        language='eazybi',
                        model='eazybi',
                        eazybi_report_id=eazybi_report.id,
                        llm_response={}
                    )
                    crud.create_analysis_result(db, analysis_result)
                    all_results.append({"report_name": report_config.name, "status": "Processed"})
                else:
                    all_results.append({"report_name": report_config.name, "status": "No query_results found"})

            except httpx.RequestError as exc:
                all_results.append({"report_name": report_config.name, "error": f"Request error: {exc}"})
            except httpx.HTTPStatusError as exc:
                all_results.append({"report_name": report_config.name, "error": f"HTTP status error: {exc.response.status_code}"})
            except Exception as exc:
                all_results.append({"report_name": report_config.name, "error": f"An unexpected error occurred: {exc}"})
    
    return {"results": all_results}

@router.get("/report/{report_id}")
async def get_specific_eazybi_report(report_id: str, db: Session = Depends(get_db)):
    username = settings.EAZYBI_USERNAME
    password = settings.EAZYBI_PASSWORD

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eazybi credentials not configured."
        )

    auth_string = f"{username}:{password}"
    encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_auth_string}"}

    eazybi_url = f"{settings.EAZYBI_BASE_URL}/{report_id}.json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(eazybi_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "query_results" in data:
                return {"report_id": report_id, "result": data["query_results"]}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No query_results found for this report."
                )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request error for report {report_id}: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"HTTP status error for report {report_id}: {exc.response.status_code}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred for report {report_id}: {exc}"
        )
