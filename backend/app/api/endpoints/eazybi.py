from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.config import settings
import httpx
import base64
import json
import os

router = APIRouter()

EAZYBI_CONFIG_PATH = "/app/app/core/eazybi_config.json"

@router.get("/eazybi-data")
async def get_eazybi_data():
    username = settings.EAZYBI_USERNAME
    password = settings.EAZYBI_PASSWORD

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eazybi credentials not configured in environment variables."
        )

    # Basic Authentication header
    auth_string = f"{username}:{password}"
    encoded_auth_string = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_auth_string}"}

    all_results = []

    try:
        with open(EAZYBI_CONFIG_PATH, "r") as f:
            eazybi_reports_config = json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eazybi configuration file not found at {EAZYBI_CONFIG_PATH}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error decoding Eazybi configuration file at {EAZYBI_CONFIG_PATH}. Invalid JSON."
        )

    async with httpx.AsyncClient() as client:
        for report_config in eazybi_reports_config:
            report_name = report_config.get("name", "Unknown Report")
            report_id = report_config.get("report_id")

            if not report_id:
                all_results.append({"report_name": report_name, "error": "Missing report_id in configuration."})
                continue

            eazybi_url = f"{settings.EAZYBI_BASE_URL}/{report_id}.json"

            try:
                response = await client.get(eazybi_url, headers=headers)
                response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
                data = response.json()

                # Correctly parse the Eazybi API response
                if "query_results" in data and isinstance(data["query_results"], dict):
                    
                    report_data = data["query_results"]
                    all_results.append({"report_name": report_name, "result": report_data})
                else:
                    all_results.append({"report_name": report_name, "result": "No query_results found or unexpected data format."})

            except httpx.RequestError as exc:
                all_results.append({
                    "report_name": report_name,
                    "error": f"An error occurred while requesting Eazybi API: {exc}"
                })
            except httpx.HTTPStatusError as exc:
                all_results.append({
                    "report_name": report_name,
                    "error": f"Eazybi API returned an error: {exc.response.status_code} - {exc.response.text}"
                })
            except Exception as exc:
                all_results.append({
                    "report_name": report_name,
                    "error": f"An unexpected error occurred: {exc}"
                })
    
    return {"results": all_results}

@router.get("/report/{report_id}")
async def get_specific_eazybi_report(report_id: str):
    username = settings.EAZYBI_USERNAME
    password = settings.EAZYBI_PASSWORD

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eazybi credentials not configured in environment variables."
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

            if "query_results" in data and isinstance(data["query_results"], dict):
                return {"report_id": report_id, "result": data["query_results"]}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No query_results found or unexpected data format for this report."
                )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while requesting Eazybi API for report {report_id}: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Eazybi API returned an error for report {report_id}: {exc.response.status_code} - {exc.response.text}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred for report {report_id}: {exc}"
        )
