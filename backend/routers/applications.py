from fastapi import APIRouter, Query

from backend.database import get_db
from backend.models import ApplicationSummary, ApplicationDetail, ApplicationEvent

router = APIRouter()


@router.get("")
def list_applications(
    company: str | None = None,
    status: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
) -> dict:
    db = get_db()
    conditions = []
    params = []

    if company:
        conditions.append("company_name LIKE ?")
        params.append(f"%{company}%")
    if status:
        conditions.append("current_status = ?")
        params.append(status)
    if from_date:
        conditions.append("first_event_at >= ?")
        params.append(from_date)
    if to_date:
        conditions.append("last_event_at <= ?")
        params.append(to_date)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    offset = (page - 1) * per_page

    total = db.execute(f"SELECT COUNT(*) as cnt FROM applications {where}", params).fetchone()["cnt"]
    rows = db.execute(
        f"SELECT * FROM applications {where} ORDER BY last_event_at DESC LIMIT ? OFFSET ?",
        params + [per_page, offset],
    ).fetchall()
    db.close()

    apps = [ApplicationSummary(**dict(row)) for row in rows]
    return {"applications": [a.model_dump() for a in apps], "total": total, "page": page, "per_page": per_page}


@router.get("/{app_id}")
def get_application(app_id: int) -> ApplicationDetail:
    db = get_db()
    app_row = db.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    if not app_row:
        db.close()
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Application not found")

    event_rows = db.execute(
        "SELECT * FROM application_events WHERE application_id = ? ORDER BY event_date ASC",
        (app_id,),
    ).fetchall()
    db.close()

    events = [ApplicationEvent(**dict(row)) for row in event_rows]
    return ApplicationDetail(**dict(app_row), events=events)
