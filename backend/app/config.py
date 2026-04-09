from pydantic_settings import BaseSettings
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "NeoApprovements"

    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str

    REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "Lax"

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_HOST: str
    DB_PORT: int = 5432

    class Config:
        env_file = ENV_PATH
        case_sensitive = True
         
    @property
    def issuer(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/certs"

    @property
    def token_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/token"

    @property
    def auth_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/auth"

settings = Settings()