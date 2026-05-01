import json

import anthropic

from backend.config import settings
from backend.models import ParsedEmail, TriageResult

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a job application email classifier. Given an email (subject, sender, body), determine:

1. Whether this email is related to a job application process.
2. If yes, extract structured information about the application event.

Rules for event_type:
- "applied": confirmation that an application was submitted or received
- "oa_invite": online assessment or coding challenge invitation
- "phone_screen": phone screen or initial recruiter call scheduled/confirmed
- "technical_interview": technical or coding interview
- "onsite": onsite or virtual onsite multi-round interview
- "take_home": take-home assignment
- "panel": panel interview
- "hiring_manager": hiring manager interview
- "final_round": final round interview (if explicitly labeled)
- "offer": job offer extended
- "rejection": application rejected at any stage
- "withdrawn": candidate withdrew
- "follow_up": generic follow-up or status update
- "other_interview": catch-all for interview stages not covered above

Extract the company name exactly as it appears. Extract the role title if mentioned.
If the email is not job-related (newsletters, spam, general correspondence), set is_job_related to false.
For confidence, rate 0.0 to 1.0 how certain you are this classification is correct."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "is_job_related": {"type": "boolean"},
        "company_name": {"type": ["string", "null"]},
        "role_title": {"type": ["string", "null"]},
        "event_type": {"type": ["string", "null"]},
        "event_label": {"type": ["string", "null"]},
        "summary": {"type": ["string", "null"]},
        "confidence": {"type": "number"},
    },
    "required": [
        "is_job_related",
        "company_name",
        "role_title",
        "event_type",
        "event_label",
        "summary",
        "confidence",
    ],
    "additionalProperties": False,
}

BATCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": OUTPUT_SCHEMA,
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def format_email_text(email: dict) -> str:
    return f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date']}\n\n{email['body']}"


def parse_email(email: dict) -> ParsedEmail:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f"Classify this email:\n\n{format_email_text(email)}"}],
        output_config={"format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    return ParsedEmail(**json.loads(text))


TRIAGE_SYSTEM_PROMPT = """You are a job application email triage classifier. Given a batch of email metadata (subject, sender, snippet only), determine whether each email is likely related to a job application process.

You are looking for: application confirmations, interview scheduling, recruiter outreach about specific roles, offer letters, rejections, assessment invitations, background checks, and similar job-search correspondence.

You are NOT looking for: newsletters, marketing, social media notifications, financial offers, subscription confirmations, product updates, or general correspondence that happens to mention words like "role" or "position".

For each email, return whether it is likely relevant and your confidence (0.0 to 1.0)."""

TRIAGE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "likely_relevant": {"type": "boolean"},
                    "confidence": {"type": "number"},
                },
                "required": ["index", "likely_relevant", "confidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def triage_emails_batch(emails: list[dict]) -> list[TriageResult]:
    if not emails:
        return []

    emails_text = "\n\n".join(
        f"[Email {i}]\nSubject: {e['subject']}\nFrom: {e['sender']}\nSnippet: {e['snippet']}"
        for i, e in enumerate(emails)
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=[{"type": "text", "text": TRIAGE_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f"Triage these {len(emails)} emails:\n\n{emails_text}"}],
        output_config={"format": {"type": "json_schema", "schema": TRIAGE_OUTPUT_SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)

    results = []
    for item in data["results"]:
        idx = item["index"]
        if 0 <= idx < len(emails):
            results.append(TriageResult(
                gmail_message_id=emails[idx]["gmail_message_id"],
                likely_relevant=item["likely_relevant"],
                confidence=item["confidence"],
            ))
    return results


def parse_email_batch(emails: list[dict]) -> list[ParsedEmail]:
    if len(emails) == 1:
        return [parse_email(emails[0])]

    emails_text = "\n\n---EMAIL SEPARATOR---\n\n".join(
        f"[Email {i + 1}]\n{format_email_text(e)}" for i, e in enumerate(emails)
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT
                + "\n\nYou will receive multiple emails separated by '---EMAIL SEPARATOR---'. "
                "Return a JSON object with a 'results' array containing one result per email, in the same order.",
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": f"Classify these emails:\n\n{emails_text}"}],
        output_config={"format": {"type": "json_schema", "schema": BATCH_OUTPUT_SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    return [ParsedEmail(**r) for r in data["results"]]
