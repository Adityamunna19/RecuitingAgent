# Recruiter Agent (Resume Analysis + Google Meet Scheduling)

This project analyzes a resume against a job description using Azure OpenAI, then (if the score is above a threshold) lets a recruiter pick an interview date/time and sends a Google Meet invite via Google Calendar.

## Features

- Resume analysis with Azure OpenAI (returns JSON with score/verdict).
- Automatic email extraction from resume text.
- Recruiter-controlled scheduling with IST datetime picker.
- Google Calendar invite with Meet link sent to the candidate.

## Tech Stack

- Backend: FastAPI, LangChain, Azure OpenAI
- Frontend: HTML + JavaScript
- Google Calendar API for Meet invite

## Prerequisites

- Python 3.11+ recommended (Python 3.14 may show warnings with LangChain/Pydantic).
- A Google account (for Calendar/Meet).
- Azure OpenAI resource + deployment.

## 1) Clone and Setup Environment

```bash
cd /path/to/your/workspace
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

## 2) Configure Azure OpenAI

Create a `.env` file in `backend/`:

```env
AZURE_OPENAI_API_KEY=YOUR_AZURE_OPENAI_KEY
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

## 3) Google Cloud Setup (OAuth)

Use a single Google account and authorize the app locally.

### Steps
1. Create a Google Cloud project.
2. Enable **Google Calendar API**.
3. Configure **OAuth consent screen** (External) and add yourself as a **Test user**.
4. Create **OAuth client ID** (Desktop app).
5. Download the credentials JSON file.

Place the file at:

```
backend/credentials.json
```

The first time you schedule, a browser window will open for authorization.  
After approval, `backend/token.json` will be created and reused.

## 4) Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

## 5) Run the Frontend

Open `frontend/index.html` in your browser.

## 6) How It Works

1. Upload resume + paste JD.
2. Backend runs Azure OpenAI analysis.
3. If score > threshold (default: 50), the UI shows a datetime picker.
4. Recruiter selects date/time and clicks **Schedule**.
5. Google Meet invite is sent to the candidate email (extracted from resume).

## Threshold

The selection threshold is set for testing:

```
backend/agents/recruiter_agent.py
threshold = 50
```

Change it to 80+ later if needed.

## API Endpoints

- `POST /analyze`  
  Form fields:
  - `resume` (file)
  - `jd` (string)

- `POST /schedule`  
  Form fields:
  - `candidate_name`
  - `candidate_email`
  - `interview_datetime` (ISO, e.g. `2026-02-07T17:30`)
  - `timezone` (default: `Asia/Kolkata`)

## Troubleshooting

**OAuth error: "Access blocked"**  
Add your Google account under **OAuth consent screen → Test users**.

**No scheduling even with high score**  
Ensure the resume includes a valid email like `name@example.com`.

**Python 3.14 warnings**  
Use Python 3.11 or 3.12 for best compatibility.

---

If you want deployment instructions (Docker, hosting, or CI), say the word.
