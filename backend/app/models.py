from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass

# =============================================
# 1. Пользователи
# =============================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)                    # "Сотрудник", "Руководитель" и т.д.
    role_type: Mapped[str] = mapped_column(String(20), nullable=False)               # user | manager | pm | admin
    avatar: Mapped[Optional[str]] = mapped_column(String(10))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    created_requests: Mapped[List["Request"]] = relationship("Request", back_populates="creator", cascade="all, delete-orphan")
    project_memberships: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    approvals: Mapped[List["RequestApprover"]] = relationship("RequestApprover", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id} ({self.name})>"


# =============================================
# 2. Проекты
# =============================================
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, server_default="0")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    members: Mapped[List["ProjectMember"]] = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.id} - {self.name}>"


# =============================================
# 3. Участие пользователей в проектах
# =============================================
class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    member_role: Mapped[str] = mapped_column(String(20), nullable=False)   # employee | manager

    # Связи
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="project_memberships")

    __table_args__ = (
        Index("ix_project_members_project_user", "project_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<ProjectMember {self.user_id} in {self.project_id} as {self.member_role}>"


# =============================================
# 4. Типы запросов (встроенные + кастомные)
# =============================================
class RequestType(Base):
    __tablename__ = "request_types"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, unique=True)   # leave, budget_change, rt_001...
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    fields_config: Mapped[dict] = mapped_column(JSONB, nullable=False)           # настройки формы
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSONB)                # доп. поля
    created_by_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())

    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self):
        return f"<RequestType {self.id} - {self.name}>"


# =============================================
# 5. Запросы на согласование
# =============================================
class Request(Base):
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(ForeignKey("request_types.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    approval_type: Mapped[str] = mapped_column(String(20), nullable=False)       # unanimous | any
    status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")  # pending | approved | rejected
    details: Mapped[Optional[dict]] = mapped_column(JSONB)                      # все динамические данные
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    creator: Mapped["User"] = relationship("User", back_populates="created_requests")
    approvers: Mapped[List["RequestApprover"]] = relationship("RequestApprover", back_populates="request", cascade="all, delete-orphan")
    history: Mapped[List["RequestHistory"]] = relationship("RequestHistory", back_populates="request", cascade="all, delete-orphan")
    request_type: Mapped["RequestType"] = relationship("RequestType")

    def __repr__(self):
        return f"<Request {self.id} - {self.title}>"


# =============================================
# 6. Согласующие и их решения
# =============================================
class RequestApprover(Base):
    __tablename__ = "request_approvers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision: Mapped[Optional[bool]] = mapped_column(Boolean)                    # NULL = pending, True = approved, False = rejected
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Связи
    request: Mapped["Request"] = relationship("Request", back_populates="approvers")
    user: Mapped["User"] = relationship("User", back_populates="approvals")

    __table_args__ = (
        Index("ix_request_approvers_request_user", "request_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<RequestApprover {self.user_id} on {self.request_id} → {self.decision}>"


# =============================================
# 7. История всех действий
# =============================================
class RequestHistory(Base):
    __tablename__ = "request_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)              # created, approved, rejected, resubmitted...
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    note: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), server_default=func.now())

    # Связи
    request: Mapped["Request"] = relationship("Request", back_populates="history")
    user: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self):
        return f"<History {self.action} on {self.request_id}>"


# =============================================
# Индексы для производительности
# =============================================
Index("ix_requests_creator_status", Request.creator_id, Request.status)
Index("ix_requests_type_status", Request.type, Request.status)
Index("ix_request_history_request", RequestHistory.request_id)