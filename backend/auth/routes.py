from fastapi import APIRouter, Request
from auth.service import exchange_code
from config import settings
from fastapi.responses import RedirectResponse
from urllib.parse import unquote


router = APIRouter()

@router.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    tokens = exchange_code(code)

    redirect_url = unquote(state) if state else "/"

    response = RedirectResponse(redirect_url)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    return response