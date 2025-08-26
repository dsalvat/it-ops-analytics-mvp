from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

class LLMRequest(BaseModel):
    prompt: str
    context: str

@router.post("/generate")
async def generate_text(request: LLMRequest):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(request.prompt, context=request.context)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calling the Gemini API: {e}"
        )