from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from backend.config import settings
from backend.gmail_auth import (
    create_auth_url,
    handle_callback,
    get_credentials,
    get_user_email,
    clear_token,
)
from backend.models import AuthStatus

router = APIRouter()


@router.get("/status")
def auth_status() -> AuthStatus:
    creds = get_credentials()
    if creds is None:
        return AuthStatus(authenticated=False)
    email = get_user_email(creds)
    return AuthStatus(authenticated=True, email=email)


@router.get("/login")
def auth_login():
    auth_url, _ = create_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def auth_callback(code: str, state: str):
    handle_callback(code, state)
    return RedirectResponse(url=f"{settings.frontend_url}/settings?auth=success")


@router.post("/logout")
def auth_logout():
    clear_token()
    return {"status": "logged_out"}
