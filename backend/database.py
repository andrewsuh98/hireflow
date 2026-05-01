import sqlite3
from backend.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS processed_emails (
    gmail_message_id TEXT PRIMARY KEY,
    processed_at     TEXT NOT NULL DEFAULT (datetime('now')),
    was_relevant     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sync_runs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at     TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at    TEXT,
    emails_fetched INTEGER DEFAULT 0,
    emails_parsed  INTEGER DEFAULT 0,
    events_created INTEGER DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS applications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name    TEXT NOT NULL,
    role_title      TEXT,
    current_status  TEXT NOT NULL DEFAULT 'applied',
    first_event_at  TEXT NOT NULL,
    last_event_at   TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(company_name, role_title)
);

CREATE TABLE IF NOT EXISTS application_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id   INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    gmail_message_id TEXT NOT NULL,
    event_type       TEXT NOT NULL,
    event_label      TEXT,
    event_date       TEXT NOT NULL,
    summary          TEXT,
    raw_subject      TEXT,
    raw_from         TEXT,
    raw_snippet      TEXT,
    confidence       REAL DEFAULT 1.0,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_app_id ON application_events(application_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON application_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_date ON application_events(event_date);
CREATE INDEX IF NOT EXISTS idx_apps_company ON applications(company_name);
CREATE INDEX IF NOT EXISTS idx_apps_status ON applications(current_status);

CREATE TABLE IF NOT EXISTS auth_tokens (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    token_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_db() -> sqlite3.Connection:
    settings.db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(settings.db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.close()
