from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import openai
import os
import google.generativeai as genai
from app.core.config import settings
import logging
from app.core.prompts import PROMPTS
from app import crud, schemas
from app.core.database import get_db

logging.basicConfig(level=logging.INFO)

router = APIRouter()



class LLMFinalReportRequest(BaseModel):
    data: list[str]

@router.post("/generate")
async def generate_text(report_id: str = Query(...), prompt: str = Query(...), db: Session = Depends(get_db),
                        platform: str = Query("OpenAI", enum=["OpenAI", "Gemini"]),
                        model: str = Query("gpt-3.5-turbo"),
                        language: str = Query("English", enum=["English", "Català", "Castellano"]),
                        week: int = Query(None),
                        year: int = Query(None),
                        prompt_name: str = Query("it_operations_analyst")):
    if prompt_name not in PROMPTS:
        raise HTTPException(status_code=400, detail="Prompt not found.")

    prompt_template = PROMPTS[prompt_name]

    eazybi_analysis_result = crud.get_analysis_result(db, report_id=report_id, week=week, year=year, language='eazybi', model='eazybi')
    if not eazybi_analysis_result or not eazybi_analysis_result.eazybi_report:
        raise HTTPException(status_code=404, detail="EazyBI data not found for this report, week, and year.")

    context = eazybi_analysis_result.eazybi_report.report_data

    if platform == "OpenAI":
        response_text = await generate_openai(report_id, prompt, model, language, week, year, prompt_template, context)
    elif platform == "Gemini":
        response_text = await generate_gemini(report_id, prompt, model, language, week, year, prompt_template, context)

    logging.info(f"LLM Response to be saved: {response_text}")

    analysis_result = crud.get_analysis_result(db, report_id=report_id, week=week, year=year, language=language, model=model)

    if analysis_result:
        analysis_update = schemas.AnalysisResultUpdate(llm_response=response_text)
        crud.update_analysis_result(db, db_analysis_result=analysis_result, analysis_result=analysis_update)
    else:
        analysis_create = schemas.AnalysisResultCreate(
            report_id=report_id,
            week=week,
            year=year,
            language=language,
            model=model,
            eazybi_report_id=eazybi_analysis_result.eazybi_report_id,
            llm_response=response_text
        )
        crud.create_analysis_result(db, analysis_result=analysis_create)

    return {"response": response_text}

async def generate_openai(report_id: str, prompt: str, model: str, language: str, week: int, year: int, prompt_template: str, context: str):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt_it_analyst_complete = prompt_template.format(language=language, week=week, year=year)

        full_prompt = "Context: {}. \n\nPrompt: {} **Data**: {}".format(prompt_it_analyst_complete, prompt, context)
        logging.info(f"Request Prompt: {full_prompt}")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model=model,
        )
        
        response_text = chat_completion.choices[0].message.content
        logging.info(f"OpenAI Response: {response_text}")
        return response_text

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calling the OpenAI API: {e}"
        )

async def generate_gemini(report_id: str, prompt: str, model: str, language: str, week: int, year: int, prompt_template: str, context: str):
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        gemini_model = genai.GenerativeModel(model)

        prompt_it_analyst_complete = f"""
### **Prompt for the Language Model: IT Operations Analyst**

**Assigned Role:** IT Operations Analyst for a supermarket chain. Your function is strictly analytical, not operational. Your objective is to use the provided data to evaluate the quality of IT service and propose strategic improvements.

---

**Business and Operations Context:**

*   **Company:** Supermarket chain specializing in high-quality fruits and vegetables.
*   **Locations:** 148 stores in total (145 in Catalonia and 3 in Andorra).
*   **Ticket Volume:** A high volume of 400-500 tickets per week.
*   **IT Department Structure:** Composed of 9 specialized teams, based in a central office. All teams, except for the **Systems** team, have the flexibility to work remotely some days.

---

**Key Analytical Responsibilities and Tasks:**

You must process and analyze Jira ticket data, which will be provided to you in JSON format. Your analysis must cover the following metrics and criteria:

1.  **Data Integrity in Tickets:**
    *   Verify the completeness of the following mandatory fields in each ticket:
        *   "Equip IT" (IT Team)
        *   "Reporter"
        *   "Assignee"
        *   "Customer Unit" (Beneficiary)
    *   Calculate the percentage of tickets that meet this completeness for a given period (daily, weekly, monthly).

2.  **SLA Compliance (Time to First Response - TTFR):**
    *   Calculate the percentage of tickets that comply with the Time to First Response SLA, based on the following priority table:
        *   **Incidents:**
            *   **P1 - MUST (Critical):** 1 hour
            *   **P2 - SHOULD (High):** 2 hours
            *   **P3 - COULD (Medium):** 4 hours
            *   **P4-WOULD / P5 - PENDENT:** 12 hours
        *   **Service Request:**
            *   **P1-MUST/P2 - SHOULD:** 8 hours
            *   **P3 - COULD (Medium):** 24 hours
            *   **P4-WOULD/P5-PENDENT:** 48 hours
        *   **Other:** 96 hours

3.  **User Satisfaction Analysis:**
    *   Determine the average user satisfaction. The goal is $\ge4.7/5$.
    *   Calculate the completion rate of surveys, both overall and for each team. The goal is a minimum of 10% of surveys completed.

4.  **Resolution Time Analysis:**
    *   Analyze and break down the average resolution times by the following categories, both overall and for each team:
        *   "Request Type"
        *   "Issue Type"
        *   "Priority"

5.  **Quality of Resolutions:**
    *   Verify that the resolutions contain a clear explanation of what happened and how the problem was resolved.
    *   For tickets classified as "Change Request" or "Project", confirm that the requirements are clearly defined.

---

**Reporting and Communication Structure (Response Format):**

Your response must generate a structured and clear report, which serves as a direct deliverable. Depending on the frequency of the analysis (daily, weekly, monthly), the structure should be adapted:

*   **For a Daily Analysis:**
    *   **Subject:** [DAILY] IT Operational Analysis - [DATE]
    *   **Structure:** Executive Summary (3-4 lines), Metrics of the Day (tickets created/resolved/pending, SLA compliance), and Alerts and Required Actions (tickets out of SLA, overloaded teams).

*   **For a Weekly Analysis:**
    *   **Subject:** [WEEKLY] IT Operational Analysis - Week {week} {year}
    *   **Structure:** Weekly Dashboard, Detailed Analysis by Team (performance, resolution times), Pattern Identification (recurring problems, bottlenecks), and Priority Recommendations (Top 3 actions per team).

*   **For a Monthly Analysis:**
    *   **Subject:** [MONTHLY] IT Operational Analysis - [MONTH] [YEAR]
    *   **Structure:** Executive Summary (key KPIs, monthly comparison), Deep Dive by Dimensions (by Request/Issue/Priority), Quality Analysis (reopened tickets, incomplete documentation), and Strategic Proposals (improvement projects, optimizations).

---

**Considerations and Analysis Philosophy:**

*   **Focus:** Prioritize a quantitative approach (statistical analysis) complemented by a qualitative approach (quality of resolution).
*   **Impact Quantification:** Use the **MoSCoW matrix** to size the impact of the problems:
    *   **P1 (MUST):** Affects 50-100% of users, prevents critical tasks.
    *   **P2 (SHOULD):** Affects 30-50% of users, allows tasks with difficulty.
    *   **P3 - COULD (Medium):** Affects 10-30% of users, affects non-critical functionalities.
    *   **P4 (WOULD):** Affects 1-10% of users.
    *   **P5 (WON'T):** Affects 1 or a few users, aesthetic.
*   **Communication:** Be direct but empathetic. Focus communication on solutions, not problems. All recommendations must be backed by objective data.
*   **Role Limitations:** Remember that you only analyze and recommend. You do **not** monitor infrastructure, you do **not** manage incidents directly, you do **not** make executive decisions or execute corrective actions.

**Output Language:** Please generate the response in {language}.
"""
        full_prompt = "Context: {}. \n\nPrompt: {} **Data**: {}".format(prompt_it_analyst_complete, prompt, context)
        logging.info(f"Request Prompt: {full_prompt}")
        response = gemini_model.generate_content(full_prompt)
        
        logging.info(f"Gemini Response: {response.text}")
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calling the Gemini API: {e}"
        )

@router.post("/generate_final_report")
async def generate_final_report(request: LLMFinalReportRequest, db: Session = Depends(get_db),
                                platform: str = Query("OpenAI", enum=["OpenAI", "Gemini"]),
                                model: str = Query("gpt-3.5-turbo"), language: str = Query("English", enum=["English", "Català", "Castellano"]),
                                week: int = Query(None),
                                year: int = Query(None)):
    prompt_template = PROMPTS["final_report_context_prompt"]
    
    data_context = "\n".join(request.data)
    
    if platform == "OpenAI":
        response_text = await generate_openai_final_report(model, language, week, year, prompt_template, data_context)
    elif platform == "Gemini":
        response_text = await generate_gemini_final_report(model, language, week, year, prompt_template, data_context)

    # Check if a final report already exists for this week and year
    existing_report = crud.get_report_by_week_year(db, week=week, year=year)

    if existing_report:
        # Update the existing report
        report_update = schemas.ReportUpdate(report_data=response_text, status="final")
        crud.update_report(db, db_report=existing_report, report=report_update)
    else:
        # Create a new final report
        report_create = schemas.ReportCreate(
            week=week,
            year=year,
            report_data=response_text,
            status="final"
        )
        crud.create_report(db, report=report_create)

    return {"response": response_text}

async def generate_openai_final_report(model: str, language: str, week: int, year: int, prompt_template: str, data_context: str):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        formatted_prompt = prompt_template.format(language=language, week=week, year=year)
        
        full_prompt = f"Context: {formatted_prompt}\n\nData: {data_context}"
        logging.info(f"Request Prompt: {full_prompt}")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model=model,
        )
        
        response_text = chat_completion.choices[0].message.content
        logging.info(f"OpenAI Response: {response_text}")
        return response_text

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calling the OpenAI API: {e}"
        )

async def generate_gemini_final_report(model: str, language: str, week: int, year: int, prompt_template: str, data_context: str):
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        gemini_model = genai.GenerativeModel(model)

        formatted_prompt = prompt_template.format(language=language, week=week, year=year)

        full_prompt = f"Context: {formatted_prompt}\n\nData: {data_context}"
        logging.info(f"Request Prompt: {full_prompt}")
        response = gemini_model.generate_content(full_prompt)
        
        logging.info(f"Gemini Response: {response.text}")
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calling the Gemini API: {e}"
        )
