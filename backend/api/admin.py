from fastapi import APIRouter, Depends
from auth.roles import require_roles

router = APIRouter()


@router.get("/admin")
def admin(user=Depends(require_roles(["admin"]))):
    return {"msg": "admin access"}