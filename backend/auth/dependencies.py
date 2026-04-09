from fastapi import Request
from fastapi.responses import RedirectResponse
from jwt import InvalidTokenError
from auth.security import verify_jwt
from auth.service import refresh_token_flow
from config import settings
from urllib.parse import quote

def redirect_to_login(request: Request):
    original_url = str(request.url)

    login_url = (
        f"{settings.auth_url}"
        f"?client_id={settings.KEYCLOAK_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid"
        f"&redirect_uri={settings.REDIRECT_URI}"
        f"&state={quote(original_url)}"
    )

    return RedirectResponse(login_url)

def get_token_from_request(request: Request):
    return request.cookies.get("access_token")

def get_refresh_token_from_request(request: Request):
    return request.cookies.get("refresh_token")

def auth_dependency(request: Request):
    access_token = get_token_from_request(request)
    refresh_token = get_refresh_token_from_request(request)

    if not access_token:
        return redirect_to_login(request)

    try:
        payload = verify_jwt(access_token)
        request.state.user = payload
        return payload
    except InvalidTokenError:
        if not refresh_token:
            return redirect_to_login(request)

        new_tokens = refresh_token_flow(refresh_token)
    
        if "access_token" not in new_tokens:
            return redirect_to_login(request)

        response = RedirectResponse(request.url)
        response.set_cookie(
            key="access_token",
            value=new_tokens["access_token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
        response.set_cookie(
            key="refresh_token",
            value=new_tokens["refresh_token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
        return response