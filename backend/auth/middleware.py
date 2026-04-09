from starlette.middleware.base import BaseHTTPMiddleware
from auth.dependencies import auth_dependency
from fastapi import Response

AUTH_PATH = ("/api")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith(AUTH_PATH):
            result = auth_dependency(request)
            if isinstance(result, Response):
                return result

            request.state.user = result

        response = await call_next(request)
        return response
