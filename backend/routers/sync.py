import logging

from fastapi import APIRouter, BackgroundTasks

logger = logging.getLogger(__name__)

from backend.database import get_db
from backend.gmail_auth import get_credentials
from backend.gmail_fetch import (
    get_gmail_service,
    build_query,
    fetch_message_ids,
    fetch_message_metadata,
    fetch_message_content,
)
from backend.ai_parser import parse_email_batch
from backend.models import (
    SyncRequest,
    SyncStatus,
    ProcessRequest,
    DismissRequest,
    StagedEmailResponse,
    StagedEmailResult,
)

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


def _get_staged_ids() -> set[str]:
    db = get_db()
    rows = db.execute("SELECT gmail_message_id FROM staged_emails").fetchall()
    db.close()
    return {row["gmail_message_id"] for row in rows}


def _mark_processed(gmail_message_id: str, was_relevant: bool, subject: str = "", sender: str = "", date: str = "", snippet: str = ""):
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO processed_emails (gmail_message_id, was_relevant, subject, sender, date, snippet) VALUES (?, ?, ?, ?, ?, ?)",
        (gmail_message_id, int(was_relevant), subject, sender, date, snippet),
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


# Phase 1: Fetch metadata only
def run_fetch(start_date: str):
    global _sync_state
    _sync_state = {"running": True, "progress": {"fetched": 0, "parsed": 0, "total": 0}}

    try:
        creds = get_credentials()
        if creds is None:
            logger.error("No valid Gmail credentials found")
            _sync_state["running"] = False
            return

        service = get_gmail_service(creds)
        query = build_query(start_date)
        all_ids = fetch_message_ids(service, query)
        logger.info(f"Found {len(all_ids)} total emails")

        processed = _get_processed_ids()
        staged = _get_staged_ids()
        new_ids = [mid for mid in all_ids if mid not in processed and mid not in staged]
        logger.info(f"New emails to fetch metadata for: {len(new_ids)}")

        _sync_state["progress"]["total"] = len(new_ids)

        db = get_db()
        for mid in new_ids:
            meta = fetch_message_metadata(service, mid)
            db.execute(
                "INSERT OR IGNORE INTO staged_emails (gmail_message_id, subject, sender, date, snippet) VALUES (?, ?, ?, ?, ?)",
                (meta["id"], meta["subject"], meta["from"], meta["date"], meta["snippet"]),
            )
            _sync_state["progress"]["fetched"] += 1

        db.commit()
        db.close()
    except Exception as e:
        logger.exception(f"Fetch failed: {e}")
        raise
    finally:
        _sync_state["running"] = False


# Phase 2: Process selected emails with AI
def run_process(gmail_message_ids: list[str]):
    global _sync_state
    _sync_state = {"running": True, "progress": {"fetched": 0, "parsed": 0, "total": len(gmail_message_ids)}}
    run_id = _create_sync_run()
    events_created = 0

    try:
        creds = get_credentials()
        if creds is None:
            logger.error("No valid Gmail credentials found")
            _finish_sync_run(run_id, 0, 0, 0, "failed")
            _sync_state["running"] = False
            return

        db = get_db()
        staged_rows = db.execute(
            f"SELECT * FROM staged_emails WHERE gmail_message_id IN ({','.join('?' * len(gmail_message_ids))})",
            gmail_message_ids,
        ).fetchall()
        staged_meta = {row["gmail_message_id"]: dict(row) for row in staged_rows}
        db.close()

        service = get_gmail_service(creds)

        for batch_ids in _chunk(gmail_message_ids, 5):
            messages = [fetch_message_content(service, mid) for mid in batch_ids]
            _sync_state["progress"]["fetched"] += len(messages)

            results = parse_email_batch(messages)
            for msg, parsed in zip(messages, results):
                if parsed.is_job_related:
                    _upsert_application_event(parsed, msg)
                    events_created += 1

                meta = staged_meta.get(msg["id"], {})
                _mark_processed(
                    msg["id"],
                    parsed.is_job_related,
                    meta.get("subject", msg.get("subject", "")),
                    meta.get("sender", msg.get("from", "")),
                    meta.get("date", msg.get("date", "")),
                    meta.get("snippet", msg.get("snippet", "")),
                )
                _sync_state["progress"]["parsed"] += 1

            db = get_db()
            db.execute(
                f"DELETE FROM staged_emails WHERE gmail_message_id IN ({','.join('?' * len(batch_ids))})",
                list(batch_ids),
            )
            db.commit()
            db.close()

        _finish_sync_run(run_id, len(gmail_message_ids), len(gmail_message_ids), events_created)
    except Exception as e:
        logger.exception(f"Process failed: {e}")
        _finish_sync_run(run_id, _sync_state["progress"]["fetched"], _sync_state["progress"]["parsed"], events_created, "failed")
        raise
    finally:
        _sync_state["running"] = False


@router.post("/fetch")
def sync_fetch(req: SyncRequest, background_tasks: BackgroundTasks):
    if _sync_state["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(run_fetch, req.start_date)
    return {"status": "started"}


@router.get("/staged")
def get_staged_emails() -> dict:
    db = get_db()

    staged_rows = db.execute(
        "SELECT gmail_message_id, subject, sender, date, snippet FROM staged_emails ORDER BY fetched_at DESC"
    ).fetchall()

    processed_rows = db.execute(
        """
        SELECT pe.gmail_message_id, pe.was_relevant, pe.subject, pe.sender, pe.date, pe.snippet,
               ae.event_type, a.company_name, a.role_title
        FROM processed_emails pe
        LEFT JOIN application_events ae ON pe.gmail_message_id = ae.gmail_message_id
        LEFT JOIN applications a ON ae.application_id = a.id
        ORDER BY pe.processed_at DESC
        LIMIT 200
        """
    ).fetchall()
    db.close()

    emails = []
    for row in staged_rows:
        emails.append(StagedEmailResponse(
            gmail_message_id=row["gmail_message_id"],
            subject=row["subject"] or "",
            sender=row["sender"] or "",
            date=row["date"] or "",
            snippet=row["snippet"] or "",
            status="new",
        ))

    for row in processed_rows:
        status = "processed_relevant" if row["was_relevant"] else "processed_irrelevant"
        result = None
        if row["was_relevant"] and row["event_type"]:
            result = StagedEmailResult(
                event_type=row["event_type"],
                company_name=row["company_name"] or "",
                role_title=row["role_title"],
            )
        emails.append(StagedEmailResponse(
            gmail_message_id=row["gmail_message_id"],
            subject=row["subject"] or "",
            sender=row["sender"] or "",
            date=row["date"] or "",
            snippet=row["snippet"] or "",
            status=status,
            result=result,
        ))

    return {"emails": [e.model_dump() for e in emails]}


@router.post("/process")
def sync_process(req: ProcessRequest, background_tasks: BackgroundTasks):
    if _sync_state["running"]:
        return {"status": "already_running"}
    if not req.gmail_message_ids:
        return {"status": "no_emails_selected"}
    background_tasks.add_task(run_process, req.gmail_message_ids)
    return {"status": "started"}


@router.post("/dismiss")
def sync_dismiss(req: DismissRequest):
    if not req.gmail_message_ids:
        return {"status": "no_emails_selected"}

    db = get_db()
    staged_rows = db.execute(
        f"SELECT gmail_message_id, subject, sender, date, snippet FROM staged_emails WHERE gmail_message_id IN ({','.join('?' * len(req.gmail_message_ids))})",
        req.gmail_message_ids,
    ).fetchall()

    for row in staged_rows:
        db.execute(
            "INSERT OR IGNORE INTO processed_emails (gmail_message_id, was_relevant, subject, sender, date, snippet) VALUES (?, 0, ?, ?, ?, ?)",
            (row["gmail_message_id"], row["subject"], row["sender"], row["date"], row["snippet"]),
        )

    db.execute(
        f"DELETE FROM staged_emails WHERE gmail_message_id IN ({','.join('?' * len(req.gmail_message_ids))})",
        req.gmail_message_ids,
    )
    db.commit()
    db.close()
    return {"status": "dismissed", "count": len(staged_rows)}


@router.get("/status")
def sync_status() -> SyncStatus:
    return SyncStatus(running=_sync_state["running"], progress=_sync_state["progress"])


# Keep legacy endpoint for backward compatibility
@router.post("/start")
def sync_start(req: SyncRequest, background_tasks: BackgroundTasks):
    if _sync_state["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(run_fetch, req.start_date)
    return {"status": "started"}
