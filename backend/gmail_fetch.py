import base64
import re

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_gmail_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def build_query(start_date: str) -> str:
    date_filter = f"after:{start_date.replace('-', '/')}"
    job_keywords = (
        "subject:(application OR interview OR offer OR rejection OR "
        "assessment OR coding challenge OR onsite OR phone screen OR "
        "recruiter OR hiring OR position OR role OR candidacy OR "
        "take-home OR panel OR final round OR background check)"
    )
    return f"{date_filter} {job_keywords} -category:promotions"


def fetch_message_ids(service, query: str) -> list[str]:
    message_ids = []
    request = service.users().messages().list(userId="me", q=query, maxResults=500)
    while request is not None:
        response = request.execute()
        messages = response.get("messages", [])
        message_ids.extend(msg["id"] for msg in messages)
        request = service.users().messages().list_next(request, response)
    return message_ids


def fetch_message_content(service, message_id: str) -> dict:
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"]["headers"]}
    body_text = extract_body_text(msg["payload"])
    return {
        "id": message_id,
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "date": headers.get("date", ""),
        "body": body_text[:3000],
        "snippet": msg.get("snippet", ""),
    }


def extract_body_text(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    for part in parts:
        if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            return re.sub(r"<[^>]+>", " ", html)

    for part in parts:
        result = extract_body_text(part)
        if result:
            return result

    return ""
