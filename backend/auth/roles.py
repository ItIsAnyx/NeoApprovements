from fastapi import Depends, HTTPException
from auth.dependencies import auth_dependency
from auth.security import get_roles


def require_roles(required_roles: list):
    def checker(user=Depends(auth_dependency)):
        roles = get_roles(user)

        if any(role in roles for role in required_roles):
            return user

        raise HTTPException(status_code=403, detail="Forbidden")

    return checker