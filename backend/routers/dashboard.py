from fastapi import APIRouter

from backend.database import get_db

router = APIRouter()


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

    avg_row = db.execute(
        "SELECT AVG(julianday(e.event_date) - julianday(a.first_event_at)) as avg_days "
        "FROM application_events e JOIN applications a ON e.application_id = a.id "
        "WHERE e.event_type != 'applied' AND e.id = ("
        "  SELECT MIN(e2.id) FROM application_events e2 "
        "  WHERE e2.application_id = a.id AND e2.event_type != 'applied'"
        ")"
    ).fetchone()
    avg_days = round(avg_row["avg_days"], 1) if avg_row["avg_days"] else None

    db.close()

    return {
        "total_applications": total,
        "response_rate": round(response_rate, 1),
        "avg_days_to_response": avg_days,
        "status_counts": status_counts,
    }


@router.get("/funnel")
def dashboard_funnel() -> dict:
    db = get_db()
    rows = db.execute(
        "SELECT event_type, COUNT(DISTINCT application_id) as cnt "
        "FROM application_events GROUP BY event_type ORDER BY cnt DESC"
    ).fetchall()
    db.close()

    stages = [row["event_type"] for row in rows]
    counts = [row["cnt"] for row in rows]
    return {"stages": stages, "counts": counts}


@router.get("/timeline")
def dashboard_timeline() -> dict:
    db = get_db()
    rows = db.execute(
        "SELECT a.id, a.company_name, a.role_title, a.current_status, a.first_event_at, a.last_event_at "
        "FROM applications a ORDER BY a.first_event_at DESC LIMIT 50"
    ).fetchall()
    db.close()

    entries = [dict(row) for row in rows]
    return {"entries": entries}


@router.get("/activity")
def dashboard_activity() -> dict:
    db = get_db()
    rows = db.execute(
        "SELECT strftime('%Y-%W', event_date) as week, COUNT(*) as cnt "
        "FROM application_events GROUP BY week ORDER BY week ASC"
    ).fetchall()
    db.close()

    weeks = [row["week"] for row in rows]
    counts = [row["cnt"] for row in rows]
    return {"weeks": weeks, "counts": counts}
