import jwt
from jwt import PyJWKClient
from config import settings

jwks_client = PyJWKClient(settings.jwks_url)

def verify_jwt(token: str):
    signing_key = jwks_client.get_signing_key_from_jwt(token).key

    payload = jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience="account",
        issuer=settings.issuer,
    )

    return payload


def get_roles(payload: dict):
    return payload.get("resource_access", {}).get(settings.KEYCLOAK_CLIENT_ID, []).get("roles")