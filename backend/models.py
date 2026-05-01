from pydantic import BaseModel


class SyncRequest(BaseModel):
    start_date: str


class SyncStatus(BaseModel):
    running: bool
    progress: dict


class AuthStatus(BaseModel):
    authenticated: bool
    email: str | None = None


class ApplicationEvent(BaseModel):
    id: int
    event_type: str
    event_label: str | None
    event_date: str
    summary: str | None
    raw_subject: str | None
    raw_from: str | None
    confidence: float


class ApplicationSummary(BaseModel):
    id: int
    company_name: str
    role_title: str | None
    current_status: str
    first_event_at: str
    last_event_at: str


class ApplicationDetail(BaseModel):
    id: int
    company_name: str
    role_title: str | None
    current_status: str
    first_event_at: str
    last_event_at: str
    events: list[ApplicationEvent]


class DashboardStats(BaseModel):
    total_applications: int
    response_rate: float
    avg_days_to_response: float | None
    status_counts: dict[str, int]


class ProcessRequest(BaseModel):
    gmail_message_ids: list[str]


class DismissRequest(BaseModel):
    gmail_message_ids: list[str]


class StagedEmailResult(BaseModel):
    event_type: str
    company_name: str
    role_title: str | None = None


class StagedEmailResponse(BaseModel):
    gmail_message_id: str
    subject: str
    sender: str
    date: str
    snippet: str
    status: str
    source_tier: str | None = None
    triage_status: str | None = None
    result: StagedEmailResult | None = None


class TriageResult(BaseModel):
    gmail_message_id: str
    likely_relevant: bool
    confidence: float


class ParsedEmail(BaseModel):
    is_job_related: bool
    company_name: str | None = None
    role_title: str | None = None
    event_type: str | None = None
    event_label: str | None = None
    summary: str | None = None
    confidence: float = 1.0
