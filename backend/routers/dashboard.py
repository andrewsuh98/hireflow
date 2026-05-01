from collections import Counter
from email.utils import parsedate_to_datetime

from fastapi import APIRouter

from backend.database import get_db

router = APIRouter()


def _parse_date(raw: str):
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        return None


@router.get("/stats")
def dashboard_stats() -> dict:
    db = get_db()
    total = db.execute("SELECT COUNT(*) as cnt FROM applications").fetchone()["cnt"]

    status_rows = db.execute(
        "SELECT current_status, COUNT(*) as cnt FROM applications GROUP BY current_status"
    ).fetchall()
    status_counts = {row["current_status"]: row["cnt"] for row in status_rows}

    responded = total - status_counts.get("applied", 0)
    response_rate = (responded / total * 100) if total > 0 else 0

    response_rows = db.execute(
        "SELECT e.event_date, a.first_event_at "
        "FROM application_events e JOIN applications a ON e.application_id = a.id "
        "WHERE e.event_type != 'applied' AND e.id = ("
        "  SELECT MIN(e2.id) FROM application_events e2 "
        "  WHERE e2.application_id = a.id AND e2.event_type != 'applied'"
        ")"
    ).fetchall()
    db.close()

    deltas = []
    for row in response_rows:
        event_dt = _parse_date(row["event_date"])
        first_dt = _parse_date(row["first_event_at"])
        if event_dt and first_dt:
            delta = (event_dt - first_dt).total_seconds() / 86400
            if delta >= 0:
                deltas.append(delta)

    avg_days = round(sum(deltas) / len(deltas), 1) if deltas else None

    return {
        "total_applications": total,
        "response_rate": round(response_rate, 1),
        "avg_days_to_response": avg_days,
        "status_counts": status_counts,
    }


@router.get("/activity")
def dashboard_activity() -> dict:
    db = get_db()
    rows = db.execute("SELECT event_date FROM application_events").fetchall()
    db.close()

    monthly: Counter[str] = Counter()
    for row in rows:
        dt = _parse_date(row["event_date"])
        if dt:
            monthly[dt.strftime("%Y-%m")] += 1

    sorted_months = sorted(monthly.keys())
    return {
        "months": sorted_months,
        "counts": [monthly[m] for m in sorted_months],
    }


@router.get("/recent-activity")
def dashboard_recent_activity() -> dict:
    db = get_db()
    rows = db.execute(
        "SELECT e.event_type, e.event_date, e.summary, a.company_name, a.role_title "
        "FROM application_events e "
        "JOIN applications a ON e.application_id = a.id "
        "ORDER BY e.id DESC LIMIT 20"
    ).fetchall()
    db.close()

    entries = []
    for row in rows:
        dt = _parse_date(row["event_date"])
        entries.append({
            "event_type": row["event_type"],
            "event_date": dt.isoformat() if dt else row["event_date"],
            "summary": row["summary"],
            "company_name": row["company_name"],
            "role_title": row["role_title"],
        })

    return {"entries": entries}
