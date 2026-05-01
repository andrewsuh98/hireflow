from fastapi import APIRouter, BackgroundTasks

from backend.database import get_db
from backend.gmail_auth import get_credentials
from backend.gmail_fetch import get_gmail_service, build_query, fetch_message_ids, fetch_message_content
from backend.ai_parser import parse_email_batch
from backend.models import SyncRequest, SyncStatus

router = APIRouter()

_sync_state = {"running": False, "progress": {"fetched": 0, "parsed": 0, "total": 0}}


def _chunk(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _get_processed_ids() -> set[str]:
    db = get_db()
    rows = db.execute("SELECT gmail_message_id FROM processed_emails").fetchall()
    db.close()
    return {row["gmail_message_id"] for row in rows}


def _mark_processed(gmail_message_id: str, was_relevant: bool):
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO processed_emails (gmail_message_id, was_relevant) VALUES (?, ?)",
        (gmail_message_id, int(was_relevant)),
    )
    db.commit()
    db.close()


def _upsert_application_event(parsed, email: dict):
    if not parsed.is_job_related or not parsed.company_name:
        return

    db = get_db()
    email_date = email["date"]

    row = db.execute(
        "SELECT id FROM applications WHERE company_name = ? AND (role_title = ? OR (role_title IS NULL AND ? IS NULL))",
        (parsed.company_name, parsed.role_title, parsed.role_title),
    ).fetchone()

    if row:
        app_id = row["id"]
        db.execute(
            "UPDATE applications SET current_status = ?, last_event_at = ?, updated_at = datetime('now') WHERE id = ?",
            (parsed.event_type, email_date, app_id),
        )
    else:
        cursor = db.execute(
            "INSERT INTO applications (company_name, role_title, current_status, first_event_at, last_event_at) VALUES (?, ?, ?, ?, ?)",
            (parsed.company_name, parsed.role_title, parsed.event_type or "applied", email_date, email_date),
        )
        app_id = cursor.lastrowid

    db.execute(
        "INSERT INTO application_events (application_id, gmail_message_id, event_type, event_label, event_date, summary, raw_subject, raw_from, raw_snippet, confidence) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            app_id,
            email["id"],
            parsed.event_type or "unknown",
            parsed.event_label,
            email_date,
            parsed.summary,
            email["subject"],
            email["from"],
            email["snippet"][:200] if email.get("snippet") else None,
            parsed.confidence,
        ),
    )
    db.commit()
    db.close()


def _create_sync_run() -> int:
    db = get_db()
    cursor = db.execute("INSERT INTO sync_runs (status) VALUES ('running')")
    run_id = cursor.lastrowid
    db.commit()
    db.close()
    return run_id


def _finish_sync_run(run_id: int, fetched: int, parsed: int, events: int, status: str = "completed"):
    db = get_db()
    db.execute(
        "UPDATE sync_runs SET finished_at = datetime('now'), emails_fetched = ?, emails_parsed = ?, events_created = ?, status = ? WHERE id = ?",
        (fetched, parsed, events, status, run_id),
    )
    db.commit()
    db.close()


def run_sync(start_date: str):
    global _sync_state
    _sync_state = {"running": True, "progress": {"fetched": 0, "parsed": 0, "total": 0}}
    run_id = _create_sync_run()
    events_created = 0

    try:
        creds = get_credentials()
        if creds is None:
            _finish_sync_run(run_id, 0, 0, 0, "failed")
            _sync_state["running"] = False
            return

        service = get_gmail_service(creds)
        query = build_query(start_date)
        all_ids = fetch_message_ids(service, query)

        processed = _get_processed_ids()
        new_ids = [mid for mid in all_ids if mid not in processed]

        _sync_state["progress"]["total"] = len(new_ids)
        _sync_state["progress"]["fetched"] = 0

        for batch in _chunk(new_ids, 5):
            messages = [fetch_message_content(service, mid) for mid in batch]
            _sync_state["progress"]["fetched"] += len(messages)

            results = parse_email_batch(messages)
            for msg, parsed in zip(messages, results):
                if parsed.is_job_related:
                    _upsert_application_event(parsed, msg)
                    events_created += 1
                _mark_processed(msg["id"], parsed.is_job_related)
                _sync_state["progress"]["parsed"] += 1

        _finish_sync_run(run_id, len(new_ids), len(new_ids), events_created)
    except Exception:
        _finish_sync_run(run_id, _sync_state["progress"]["fetched"], _sync_state["progress"]["parsed"], events_created, "failed")
        raise
    finally:
        _sync_state["running"] = False


@router.post("/start")
def sync_start(req: SyncRequest, background_tasks: BackgroundTasks):
    if _sync_state["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(run_sync, req.start_date)
    return {"status": "started"}


@router.get("/status")
def sync_status() -> SyncStatus:
    return SyncStatus(running=_sync_state["running"], progress=_sync_state["progress"])
