import json

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from backend.config import settings
from backend.database import get_db

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
REDIRECT_URI = "http://localhost:8000/api/auth/callback"

_state_store: dict[str, str] = {}
_verifier_store: dict[str, str] = {}


def create_auth_url() -> tuple[str, str]:
    import hashlib, base64, secrets as _secrets

    code_verifier = _secrets.token_urlsafe(96)

    flow = Flow.from_client_secrets_file(
        str(settings.google_credentials_path),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )
    _state_store[state] = state
    _verifier_store[state] = code_verifier
    return auth_url, state


def handle_callback(code: str, state: str) -> Credentials:
    code_verifier = _verifier_store.pop(state, None)

    flow = Flow.from_client_secrets_file(
        str(settings.google_credentials_path),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state,
    )
    flow.fetch_token(code=code, code_verifier=code_verifier)
    creds = flow.credentials
    save_token(creds.to_json())
    _state_store.pop(state, None)
    return creds


def save_token(token_json: str):
    db = get_db()
    db.execute(
        "INSERT INTO auth_tokens (id, token_json, updated_at) VALUES (1, ?, datetime('now')) "
        "ON CONFLICT(id) DO UPDATE SET token_json = excluded.token_json, updated_at = datetime('now')",
        (token_json,),
    )
    db.commit()
    db.close()


def get_credentials() -> Credentials | None:
    db = get_db()
    row = db.execute("SELECT token_json FROM auth_tokens WHERE id = 1").fetchone()
    db.close()
    if not row:
        return None
    creds = Credentials.from_authorized_user_info(json.loads(row["token_json"]), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_token(creds.to_json())
    return creds


def get_user_email(creds: Credentials) -> str | None:
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=creds)
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress")


def clear_token():
    db = get_db()
    db.execute("DELETE FROM auth_tokens WHERE id = 1")
    db.commit()
    db.close()
