from auth.security import get_roles
from fastapi import Request, HTTPException, status

def require_roles(*allowed_roles):
    def dependency(request: Request):
        payload = getattr(request.state, "user", None)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        roles = get_roles(payload)
        if not any(role in roles for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        
        return payload
    return dependency