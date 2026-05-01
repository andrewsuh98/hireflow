import base64
import re

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


ATS_DOMAINS = [
    "greenhouse.io",
    "greenhouse-mail.io",
    "lever.co",
    "icims.com",
    "myworkday.com",
    "workday.com",
    "taleo.net",
    "bamboohr.com",
    "jobvite.com",
    "smartrecruiters.com",
    "ashbyhq.com",
    "dover.com",
    "hired.com",
    "wellfound.com",
    "breezy.hr",
    "recruitee.com",
    "applytojob.com",
]

SUBJECT_PHRASES = [
    "application received",
    "application status",
    "application confirmation",
    "interview scheduled",
    "interview confirmation",
    "interview invitation",
    "phone screen",
    "coding challenge",
    "take-home",
    "online assessment",
    "offer letter",
    "background check",
    "we regret",
    "not moving forward",
    "your application",
    "thank you for applying",
    "thank you for your application",
    "received your application",
    "next steps",
    "candidate portal",
]


def get_gmail_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def build_queries(start_date: str) -> list[tuple[str, str]]:
    date_filter = f"after:{start_date.replace('-', '/')}"

    ats_domains = " OR ".join(ATS_DOMAINS)
    query_a = f"{date_filter} from:({ats_domains})"

    subject_clauses = " OR ".join(f'subject:"{phrase}"' for phrase in SUBJECT_PHRASES)
    query_b = f"{date_filter} ({subject_clauses}) -category:promotions -category:social"

    return [
        (query_a, "ats_domain"),
        (query_b, "subject_pattern"),
    ]


def build_query(start_date: str) -> str:
    return build_queries(start_date)[0][0]


def extract_sender_domain(from_header: str) -> str:
    match = re.search(r"@([\w.-]+)", from_header)
    return match.group(1).lower() if match else ""


def is_ats_sender(from_header: str) -> bool:
    domain = extract_sender_domain(from_header)
    return any(domain == ats or domain.endswith("." + ats) for ats in ATS_DOMAINS)


def fetch_message_ids(service, query: str) -> list[str]:
    message_ids = []
    request = service.users().messages().list(userId="me", q=query, maxResults=500)
    while request is not None:
        response = request.execute()
        messages = response.get("messages", [])
        message_ids.extend(msg["id"] for msg in messages)
        request = service.users().messages().list_next(request, response)
    return message_ids


def fetch_message_metadata(service, message_id: str) -> dict:
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["Subject", "From", "Date"],
    ).execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"]["headers"]}
    return {
        "id": message_id,
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "date": headers.get("date", ""),
        "snippet": msg.get("snippet", ""),
    }


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
