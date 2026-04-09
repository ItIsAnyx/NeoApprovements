from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import SessionLocal
from app.models import User, Project, ProjectMember, RequestType, Request, RequestApprover, RequestHistory
from app.auth.dependencies import get_current_user

router = APIRouter()


# ==========================================
# Pydantic схемы
# ==========================================

class UserResponse(BaseModel):
    id: str
    name: str
    role: str
    role_type: str
    avatar: Optional[str]

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: str
    name: str
    budget: float
    created_by_id: Optional[str]

    class Config:
        from_attributes = True


class ProjectMemberResponse(BaseModel):
    user_id: str
    user: UserResponse
    member_role: str

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    managers: List[UserResponse] = []
    employees: List[UserResponse] = []


class RequestTypeResponse(BaseModel):
    id: str
    name: str
    is_builtin: bool
    fields_config: dict

    class Config:
        from_attributes = True


class ApproverResponse(BaseModel):
    user_id: str
    user: UserResponse
    decision: Optional[bool]
    decided_at: Optional[datetime]
    comment: Optional[str]

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    action: str
    user_id: Optional[str]
    user: Optional[UserResponse]
    note: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class RequestResponse(BaseModel):
    id: str
    title: str
    type: str
    description: Optional[str]
    creator_id: str
    creator: UserResponse
    approval_type: str
    status: str
    details: Optional[dict]
    created_at: datetime
    approvers: List[ApproverResponse] = []
    history: List[HistoryResponse] = []

    class Config:
        from_attributes = True


class CreateRequestSchema(BaseModel):
    title: str
    type: str
    description: Optional[str] = None
    approval_type: str = "unanimous"
    details: Optional[dict] = None
    approver_ids: List[str] = []


class ApproveRequestSchema(BaseModel):
    decision: bool
    comment: Optional[str] = None


class CreateProjectSchema(BaseModel):
    name: str
    manager_ids: List[str]
    employee_ids: List[str] = []
    budget: float = 0.0


# ==========================================
# Helper функции
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# API endpoints
# ==========================================

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Получить всех пользователей"""
    return db.query(User).all()


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    """Получить все проекты"""
    return db.query(Project).all()


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Получить детализацию проекта с участниками"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()

    managers = []
    employees = []

    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            if member.member_role == "manager":
                managers.append(user)
            else:
                employees.append(user)

    return ProjectDetailResponse(
        **project.__dict__,
        managers=managers,
        employees=employees
    )


@router.get("/request-types", response_model=List[RequestTypeResponse])
async def get_request_types(db: Session = Depends(get_db)):
    """Получить все типы запросов"""
    return db.query(RequestType).filter(RequestType.is_active == True).all()


@router.get("/requests", response_model=List[RequestResponse])
async def get_requests(
        status: Optional[str] = None,
        creator_id: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить запросы с фильтрацией"""
    query = db.query(Request)

    if status:
        query = query.filter(Request.status == status)

    if creator_id:
        query = query.filter(Request.creator_id == creator_id)

    requests = query.order_by(Request.created_at.desc()).all()

    # enrich with approvers and history
    result = []
    for req in requests:
        approvers = db.query(RequestApprover).filter(
            RequestApprover.request_id == req.id
        ).all()

        history = db.query(RequestHistory).filter(
            RequestHistory.request_id == req.id
        ).order_by(RequestHistory.timestamp.desc()).all()

        req_dict = req.__dict__.copy()
        req_dict['approvers'] = approvers
        req_dict['history'] = history

        result.append(RequestResponse(**req_dict))

    return result


@router.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request(request_id: str, db: Session = Depends(get_db)):
    """Получить детализацию запроса"""
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    approvers = db.query(RequestApprover).filter(
        RequestApprover.request_id == request_id
    ).all()

    history = db.query(RequestHistory).filter(
        RequestHistory.request_id == request_id
    ).order_by(RequestHistory.timestamp.desc()).all()

    req_dict = req.__dict__.copy()
    req_dict['approvers'] = approvers
    req_dict['history'] = history

    return RequestResponse(**req_dict)


@router.post("/requests", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
        schema: CreateRequestSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Создать новый запрос"""
    from uuid import uuid4

    # Создаём запрос
    request = Request(
        id=f"req_{uuid4().hex[:8]}",
        title=schema.title,
        type=schema.type,
        description=schema.description,
        creator_id=current_user.id,
        approval_type=schema.approval_type,
        status="pending",
        details=schema.details or {}
    )
    db.add(request)
    db.flush()

    # Добавляем согласующих
    for approver_id in schema.approver_ids:
        approver = RequestApprover(
            request_id=request.id,
            user_id=approver_id,
            decision=None
        )
        db.add(approver)

    # Добавляем в историю
    history = RequestHistory(
        request_id=request.id,
        action="created",
        user_id=current_user.id,
        note="Запрос создан"
    )
    db.add(history)

    db.commit()
    db.refresh(request)

    return await get_request(request.id, db)


@router.post("/requests/{request_id}/approve")
async def approve_request(
        request_id: str,
        schema: ApproveRequestSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Согласовать или отклонить запрос"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Находим запись согласующего
    approver = db.query(RequestApprover).filter(
        RequestApprover.request_id == request_id,
        RequestApprover.user_id == current_user.id
    ).first()

    if not approver:
        raise HTTPException(status_code=403, detail="You are not an approver for this request")

    from datetime import datetime
    now = datetime.utcnow()

    # Обновляем решение
    approver.decision = schema.decision
    approver.decided_at = now
    approver.comment = schema.comment

    # Добавляем в историю
    action = "approved" if schema.decision else "rejected"
    history = RequestHistory(
        request_id=request_id,
        action=action,
        user_id=current_user.id,
        note=schema.comment or ""
    )
    db.add(history)

    # Проверяем статус запроса
    all_approvers = db.query(RequestApprover).filter(
        RequestApprover.request_id == request_id
    ).all()

    if request.approval_type == "unanimous":
        # Все должны согласовать
        if all(a.decision is not None for a in all_approvers):
            if all(a.decision == True for a in all_approvers):
                request.status = "approved"
            else:
                request.status = "rejected"
    else:  # any
        # Достаточно одного
        if any(a.decision == True for a in all_approvers):
            request.status = "approved"
        elif all(a.decision == False for a in all_approvers):
            request.status = "rejected"

    request.last_updated = now

    db.commit()

    return await get_request(request_id, db)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
        schema: CreateProjectSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Создать новый проект"""
    from uuid import uuid4

    project = Project(
        id=f"proj_{uuid4().hex[:8]}",
        name=schema.name,
        budget=schema.budget,
        created_by_id=current_user.id
    )
    db.add(project)
    db.flush()

    # Добавляем менеджеров
    for mgr_id in schema.manager_ids:
        member = ProjectMember(
            project_id=project.id,
            user_id=mgr_id,
            member_role="manager"
        )
        db.add(member)

    # Добавляем сотрудников
    for emp_id in schema.employee_ids:
        member = ProjectMember(
            project_id=project.id,
            user_id=emp_id,
            member_role="employee"
        )
        db.add(member)

    db.commit()
    db.refresh(project)

    return project


@router.get("/my-tasks", response_model=List[RequestResponse])
async def get_my_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить запросы, ожидающие моего согласования"""
    # Находим все pending approvers для текущего пользователя
    pending_approvers = db.query(RequestApprover).filter(
        RequestApprover.user_id == current_user.id,
        RequestApprover.decision.is_(None)
    ).all()

    request_ids = [a.request_id for a in pending_approvers]

    if not request_ids:
        return []

    requests = db.query(Request).filter(
        Request.id.in_(request_ids),
        Request.status == "pending"
    ).all()

    result = []
    for req in requests:
        approvers = db.query(RequestApprover).filter(
            RequestApprover.request_id == req.id
        ).all()

        history = db.query(RequestHistory).filter(
            RequestHistory.request_id == req.id
        ).order_by(RequestHistory.timestamp.desc()).all()

        req_dict = req.__dict__.copy()
        req_dict['approvers'] = approvers
        req_dict['history'] = history

        result.append(RequestResponse(**req_dict))

    return result


@router.get("/my-requests", response_model=List[RequestResponse])
async def get_my_requests(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Получить мои созданные запросы"""
    requests = db.query(Request).filter(
        Request.creator_id == current_user.id
    ).order_by(Request.created_at.desc()).all()

    result = []
    for req in requests:
        approvers = db.query(RequestApprover).filter(
            RequestApprover.request_id == req.id
        ).all()

        history = db.query(RequestHistory).filter(
            RequestHistory.request_id == req.id
        ).order_by(RequestHistory.timestamp.desc()).all()

        req_dict = req.__dict__.copy()
        req_dict['approvers'] = approvers
        req_dict['history'] = history

        result.append(RequestResponse(**req_dict))

    return result