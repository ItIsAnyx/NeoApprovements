from fastapi import APIRouter,  Depends
from auth.roles import require_roles

router = APIRouter()

@router.get("/user")
def user(payload=Depends(require_roles("test"))):
    return payload

@router.get("/user1")
def user1():
    return "user"