# routers/user.py
from fastapi import APIRouter, Request
from fastapi.responses import Response
from auth.dependencies import auth_dependency
from auth.security import get_roles

router = APIRouter()

@router.get("/user")
def user(request: Request):
    result = auth_dependency(request)

    if isinstance(result, Response):
        return result

    return result