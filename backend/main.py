from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.middleware.cors import CORSMiddleware
from utils.resume_parser import extract_text, ResumeParseError
from agents.recruiter_agent import run_recruiter_agent
from tools.scheduler_agent import schedule_interview_tool
import json

app = FastAPI()

# Allow the frontend to call the API from a different origin (e.g. localhost or file://).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(resume: UploadFile, jd: str = Form(...)):
    try:
        resume_text = extract_text(resume.file)
    except ResumeParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    agent_input = f"""
Analyze this resume and decide whether to schedule an interview.

Resume:
{resume_text}

Job Description:
{jd}
"""

    response = run_recruiter_agent(resume_text, jd)

    return {
        "agent_response": response
    }


@app.post("/analyze-batch")
async def analyze_batch(resumes: list[UploadFile] = File(...), jd: str = Form(...)):
    results = []
    for resume in resumes:
        try:
            resume_text = extract_text(resume.file)
            response = run_recruiter_agent(resume_text, jd)
            results.append(
                {
                    "filename": resume.filename,
                    "agent_response": response,
                }
            )
        except ResumeParseError as exc:
            results.append(
                {
                    "filename": resume.filename,
                    "error": str(exc),
                }
            )
    return {"results": results}


@app.post("/schedule")
async def schedule(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    interview_datetime: str = Form(...),
    timezone: str = Form("Asia/Kolkata"),
):
    try:
        tz = ZoneInfo(timezone)
        start = datetime.fromisoformat(interview_datetime)
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz)
        else:
            start = start.astimezone(tz)
        now = datetime.now(tz)
        if start <= now:
            raise HTTPException(
                status_code=400,
                detail="Interview time must be in the future (IST).",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid interview datetime.")

    schedule_raw = schedule_interview_tool.invoke(
        {
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "interview_datetime": interview_datetime,
            "timezone": timezone,
        }
    )
    response = {"schedule_raw": schedule_raw}
    try:
        response["schedule"] = json.loads(schedule_raw)
    except Exception:
        pass
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
