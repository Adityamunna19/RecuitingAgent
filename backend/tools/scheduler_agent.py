import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from langchain.tools import tool

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _get_calendar_service():
    creds = None
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    token_path = os.path.join(base_dir, "token.json")
    credentials_path = os.path.join(base_dir, "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


@tool
def schedule_interview_tool(
    candidate_name: str,
    candidate_email: str,
    interview_datetime: str,
    timezone: str = "Asia/Kolkata",
) -> str:
    """
    Schedule a Google Meet interview and email the invite to the candidate.
    """
    service = _get_calendar_service()
    tz = ZoneInfo(timezone)
    start = datetime.fromisoformat(interview_datetime)
    if start.tzinfo is None:
        start = start.replace(tzinfo=tz)
    else:
        start = start.astimezone(tz)
    end = start + timedelta(minutes=30)

    event = {
        "summary": f"Interview with {candidate_name}",
        "description": "Interview scheduled via recruiter agent.",
        "start": {"dateTime": start.isoformat(), "timeZone": str(tz)},
        "end": {"dateTime": end.isoformat(), "timeZone": str(tz)},
        "attendees": [{"email": candidate_email}],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(start.timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    created = (
        service.events()
        .insert(calendarId="primary", body=event, conferenceDataVersion=1, sendUpdates="all")
        .execute()
    )

    response = {
        "interview_date": start.date().isoformat(),
        "interview_time": start.time().strftime("%H:%M"),
        "interview_mode": "Google Meet",
        "meet_link": created.get("hangoutLink"),
        "event_id": created.get("id"),
    }
    return json.dumps(response)
