import requests
from config import settings
from urllib.parse import urlencode

def exchange_code(code: str):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
        "redirect_uri": settings.REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = urlencode(data)
    response = requests.post(settings.token_url, data=payload, headers=headers, proxies={"http": None})
    return response.json()


def refresh_token_flow(refresh_token: str):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "client_secret": settings.KEYCLOAK_CLIENT_SECRET
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(settings.token_url, data=data, headers=headers, proxies={"http": None}).json()
    return response