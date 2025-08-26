from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.config import settings
import httpx
import base64

router = APIRouter()

@router.get("/eazybi-data")
async def get_eazybi_data():
    eazybi_url = "https://aod.eazybi.com/accounts/59396/export/report/1075280.json"
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

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(eazybi_url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            data = response.json()

            # Assuming the Eazybi API returns a list of results and we want the first one
            data = response.json()

            # Assuming the Eazybi API returns a list of results and we want the first one
            # Correctly parse the Eazybi API response
            if "query_results" in data and "values" in data["query_results"] and \
               isinstance(data["query_results"]["values"], list) and \
               len(data["query_results"]["values"]) > 0 and \
               isinstance(data["query_results"]["values"][0], list) and \
               len(data["query_results"]["values"][0]) > 0:
                
                first_result = data["query_results"]["values"][0][0]
                return {"firstResult": first_result}
            else:
                return {"firstResult": "No data found or unexpected data format."}

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while requesting Eazybi API: {exc}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Eazybi API returned an error: {exc.response.status_code} - {exc.response.text}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {exc}"
        )
