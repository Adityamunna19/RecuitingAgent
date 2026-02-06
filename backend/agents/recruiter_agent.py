import json
import re

from tools.resume_agent import analyze_resume_tool
from utils.email_extractor import extract_email


def run_recruiter_agent(resume_text: str, job_description: str) -> dict:
    analysis_raw = analyze_resume_tool.invoke(
        {"resume_text": resume_text, "job_description": job_description}
    )
    result: dict = {"analysis_raw": analysis_raw}

    try:
        cleaned = analysis_raw.strip()
        cleaned = re.sub(r"^```json\s*|```$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
        try:
            analysis = json.loads(cleaned)
        except Exception:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise
            analysis = json.loads(match.group(0))
        result["analysis"] = analysis
    except Exception:
        return result

    verdict = str(analysis.get("verdict", "")).strip().lower()
    score = analysis.get("score", None)
    try:
        score_val = float(score) if score is not None else None
    except Exception:
        score_val = None
    candidate_name = str(analysis.get("candidate_name", "")).strip()
    candidate_email = extract_email(resume_text)
    if candidate_email:
        result["candidate_email"] = candidate_email
    # Local testing threshold; adjust to >80 later if desired.
    threshold = 50
    should_schedule = score_val is not None and score_val > threshold
    result["should_schedule"] = should_schedule
    if should_schedule and not candidate_email:
        result["schedule_error"] = "Missing candidate email in resume text."

    return result
