"""
Скрипт инициализации базы данных демо-данными
Запуск: python -m app.init_database
"""

import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import (
    Base, User, Project, ProjectMember, RequestType,
    Request, RequestApprover, RequestHistory
)


def hash_password(password: str) -> str:
    """Простое хеширование пароля (для демо)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def create_users(session: Session) -> dict:
    """Создание пользователей из сценариев"""
    users_data = [
        # Сотрудники
        {
            "id": "pbasmanov",
            "name": "Павел Басманов",
            "role": "Сотрудник",
            "role_type": "user",
            "avatar": "PB",
            "password_hash": hash_password("123456")
        },
        # Руководители
        {
            "id": "adeev",
            "name": "Андрей Деев",
            "role": "Руководитель",
            "role_type": "manager",
            "avatar": "AD",
            "password_hash": hash_password("123456")
        },
        # Менеджеры проектов
        {
            "id": "avasulich",
            "name": "Алексей Васюлич",
            "role": "Менеджер проекта",
            "role_type": "pm",
            "avatar": "AV",
            "password_hash": hash_password("123456")
        },
        {
            "id": "divanovich",
            "name": "Дмитрий Иваныч",
            "role": "Менеджер проекта",
            "role_type": "pm",
            "avatar": "DI",
            "password_hash": hash_password("123456")
        },
        {
            "id": "ipetrovich",
            "name": "Игорь Петрович",
            "role": "Менеджер проекта",
            "role_type": "pm",
            "avatar": "IP",
            "password_hash": hash_password("123456")
        },
        {
            "id": "agavrilich",
            "name": "Антон Гаврилич",
            "role": "Менеджер проекта",
            "role_type": "pm",
            "avatar": "AG",
            "password_hash": hash_password("123456")
        },
        # Администратор
        {
            "id": "admin",
            "name": "Администратор системы",
            "role": "Администратор",
            "role_type": "admin",
            "avatar": "AD",
            "password_hash": hash_password("admin")
        }
    ]

    users = {}
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users[user_data["id"]] = user

    session.flush()
    print(f" Создано {len(users)} пользователей")
    return users


def create_projects(session: Session, users: dict) -> dict:
    """Создание проектов"""
    projects_data = [
        {
            "id": "proj_x",
            "name": "Проект X",
            "budget": 100.00,
            "created_by_id": "avasulich"
        },
        {
            "id": "proj_y",
            "name": "Проект Y",
            "budget": 50.00,
            "created_by_id": "divanovich"
        },
        {
            "id": "proj_z",
            "name": "Проект Z",
            "budget": 200.00,
            "created_by_id": "agavrilich"
        }
    ]

    projects = {}
    for proj_data in projects_data:
        project = Project(**proj_data)
        session.add(project)
        projects[proj_data["id"]] = project

    session.flush()

    # Создаем участников проектов
    project_members = [
        # Проект X - 3 менеджера
        ("proj_x", "avasulich", "manager"),
        ("proj_x", "divanovich", "manager"),
        ("proj_x", "ipetrovich", "manager"),
        # Проект Y - 2 менеджера
        ("proj_y", "avasulich", "manager"),
        ("proj_y", "divanovich", "manager"),
        # Проект Z - 1 менеджер + сотрудник
        ("proj_z", "agavrilich", "manager"),
        ("proj_z", "pbasmanov", "employee"),
    ]

    for proj_id, user_id, role in project_members:
        member = ProjectMember(
            project_id=proj_id,
            user_id=user_id,
            member_role=role
        )
        session.add(member)

    session.flush()
    print(f" Создано {len(projects)} проектов с участниками")
    return projects


def create_request_types(session: Session) -> dict:
    """Создание типов запросов"""
    types_data = [
        {
            "id": "leave",
            "name": "Заявление на отпуск",
            "is_builtin": True,
            "fields_config": {
                "fields": [
                    {"name": "start_date", "label": "Дата начала", "type": "date", "required": True},
                    {"name": "end_date", "label": "Дата окончания", "type": "date", "required": True},
                    {"name": "reason", "label": "Причина", "type": "text", "required": False}
                ]
            }
        },
        {
            "id": "budget_change",
            "name": "Изменение бюджета проекта",
            "is_builtin": True,
            "fields_config": {
                "fields": [
                    {"name": "project_id", "label": "Проект", "type": "select", "required": True},
                    {"name": "old_budget", "label": "Текущий бюджет", "type": "number", "required": True},
                    {"name": "new_budget", "label": "Новый бюджет", "type": "number", "required": True},
                    {"name": "justification", "label": "Обоснование", "type": "textarea", "required": True}
                ]
            }
        },
        {
            "id": "custom_action",
            "name": "Запрос на действие",
            "is_builtin": True,
            "fields_config": {
                "fields": [
                    {"name": "action_type", "label": "Тип действия", "type": "text", "required": True},
                    {"name": "description", "label": "Описание", "type": "textarea", "required": True},
                    {"name": "priority", "label": "Приоритет", "type": "select", "required": False}
                ]
            }
        }
    ]

    types = {}
    for type_data in types_data:
        req_type = RequestType(**type_data)
        session.add(req_type)
        types[type_data["id"]] = req_type

    session.flush()
    print(f" Создано {len(types)} типов запросов")
    return types


def create_requests_scenarios(session: Session, users: dict, projects: dict, types: dict):
    """Создание запросов по 5 сценариям из ТЗ"""
    now = datetime.utcnow()
    requests = []

    # ==========================================
    # СЦЕНАРИЙ 1: Отпуск pbasmanov согласован adeev
    # ==========================================
    req1 = Request(
        id="req_001",
        title="Отпуск - Павел Басманов (май 2026)",
        type="leave",
        description="Ежегодный оплачиваемый отпуск на 14 дней",
        creator_id="pbasmanov",
        approval_type="unanimous",
        status="approved",
        details={
            "start_date": "2026-05-01",
            "end_date": "2026-05-15",
            "reason": "Плановый отпуск"
        }
    )
    session.add(req1)
    session.flush()

    # Согласующий одобрил
    approver1 = RequestApprover(
        request_id=req1.id,
        user_id="adeev",
        decision=True,
        decided_at=now - timedelta(hours=2),
        comment="Согласовано"
    )
    session.add(approver1)

    # История
    session.add_all([
        RequestHistory(
            request_id=req1.id,
            action="created",
            user_id="pbasmanov",
            note="Запрос создан",
            timestamp=now - timedelta(hours=24)
        ),
        RequestHistory(
            request_id=req1.id,
            action="approved",
            user_id="adeev",
            note="Руководитель согласовал отпуск",
            timestamp=now - timedelta(hours=2)
        )
    ])
    requests.append(req1)

    # ==========================================
    # СЦЕНАРИЙ 2: Изменение бюджета Проекта X (единогласно, ожидание)
    # ==========================================
    req2 = Request(
        id="req_002",
        title="Изменение бюджета Проекта X: 100 → 50 руб.",
        type="budget_change",
        description="Снижение бюджета проекта в связи с оптимизацией",
        creator_id="divanovich",
        approval_type="unanimous",
        status="pending",
        details={
            "project_id": "proj_x",
            "old_budget": 100.0,
            "new_budget": 50.0,
            "justification": "Оптимизация расходов"
        }
    )
    session.add(req2)
    session.flush()

    # Три менеджера должны согласовать (пока никто не согласовал)
    for mgr_id in ["avasulich", "divanovich", "ipetrovich"]:
        approver = RequestApprover(
            request_id=req2.id,
            user_id=mgr_id,
            decision=None,  # pending
            decided_at=None
        )
        session.add(approver)

    session.add(
        RequestHistory(
            request_id=req2.id,
            action="created",
            user_id="divanovich",
            note="Запрос на изменение бюджета создан. Требуется единогласное согласование.",
            timestamp=now - timedelta(hours=12)
        )
    )
    requests.append(req2)

    # ==========================================
    # СЦЕНАРИЙ 3: Отпуск pbasmanov ОТКЛОНЕН (с возможностью редактирования)
    # ==========================================
    req3 = Request(
        id="req_003",
        title="Отпуск - Павел Басманов (апрель 2026)",
        type="leave",
        description="Запрос на отпуск в апреле",
        creator_id="pbasmanov",
        approval_type="unanimous",
        status="rejected",
        details={
            "start_date": "2026-04-15",
            "end_date": "2026-04-25",
            "reason": "Личные обстоятельства"
        }
    )
    session.add(req3)
    session.flush()

    # Руководитель отклонил
    approver3 = RequestApprover(
        request_id=req3.id,
        user_id="adeev",
        decision=False,
        decided_at=now - timedelta(hours=6),
        comment="Отказ: сотрудник должен участвовать в проекте X в эти даты"
    )
    session.add(approver3)

    # История с отметкой о причине отказа
    session.add_all([
        RequestHistory(
            request_id=req3.id,
            action="created",
            user_id="pbasmanov",
            note="Запрос создан",
            timestamp=now - timedelta(days=2)
        ),
        RequestHistory(
            request_id=req3.id,
            action="rejected",
            user_id="adeev",
            note="Отказ: сотрудник должен участвовать в проекте X в эти даты. Рекомендуется изменить даты.",
            timestamp=now - timedelta(hours=6)
        )
    ])
    requests.append(req3)

    # ==========================================
    # СЦЕНАРИЙ 4: Изменение бюджета Проекта Y (достаточно одного голоса)
    # ==========================================
    req4 = Request(
        id="req_004",
        title="Изменение бюджета Проекта Y: 50 → 500 руб.",
        type="budget_change",
        description="Увеличение бюджета для расширения функционала",
        creator_id="avasulich",
        approval_type="any",  # Достаточно одного!
        status="approved",
        details={
            "project_id": "proj_y",
            "old_budget": 50.0,
            "new_budget": 500.0,
            "justification": "Расширение функционала проекта"
        }
    )
    session.add(req4)
    session.flush()

    # Первый менеджер одобрил
    approver4_1 = RequestApprover(
        request_id=req4.id,
        user_id="avasulich",
        decision=True,
        decided_at=now - timedelta(hours=3),
        comment="Согласовано как инициатор"
    )
    session.add(approver4_1)

    # Второй менеджер еще не голосовал
    approver4_2 = RequestApprover(
        request_id=req4.id,
        user_id="divanovich",
        decision=None,
        decided_at=None
    )
    session.add(approver4_2)

    session.add_all([
        RequestHistory(
            request_id=req4.id,
            action="created",
            user_id="avasulich",
            note="Запрос создан. Достаточно одного согласующего.",
            timestamp=now - timedelta(hours=4)
        ),
        RequestHistory(
            request_id=req4.id,
            action="approved",
            user_id="avasulich",
            note="Согласовано (approval_type=any - достаточно одного голоса)",
            timestamp=now - timedelta(hours=3)
        )
    ])
    requests.append(req4)

    # ==========================================
    # СЦЕНАРИЙ 5: Админский бэкдор (менеджер недоступен)
    # ==========================================
    req5 = Request(
        id="req_005",
        title="Запуск бизнес-процесса Проекта Z",
        type="custom_action",
        description="Требуется запустить процесс, но менеджер недоступен",
        creator_id="pbasmanov",
        approval_type="unanimous",
        status="approved",
        details={
            "project_id": "proj_z",
            "action_type": "project_start",
            "priority": "high",
            "description": "Срочный запуск процесса"
        }
    )
    session.add(req5)
    session.flush()

    # Менеджер agavrilich формально добавлен, но не голосовал
    approver5_1 = RequestApprover(
        request_id=req5.id,
        user_id="agavrilich",
        decision=None,
        decided_at=None,
        comment="Менеджер недоступен"
    )
    session.add(approver5_1)

    # АДМИНСКИЙ БЭКДОР: администратор проставил согласование
    approver5_admin = RequestApprover(
        request_id=req5.id,
        user_id="admin",
        decision=True,
        decided_at=now - timedelta(minutes=10),
        comment="ADMIN_OVERRIDE: согласование проставлено администратором в обход менеджера"
    )
    session.add(approver5_admin)

    session.add_all([
        RequestHistory(
            request_id=req5.id,
            action="created",
            user_id="pbasmanov",
            note="Запрос создан",
            timestamp=now - timedelta(hours=1)
        ),
        RequestHistory(
            request_id=req5.id,
            action="admin_override",
            user_id="admin",
            note="АДМИНСКИЙ БЭКДОР: менеджер agavrilich недоступен. Согласование проставлено администратором.",
            timestamp=now - timedelta(minutes=15)
        ),
        RequestHistory(
            request_id=req5.id,
            action="approved",
            user_id="admin",
            note="Бизнес-процесс запущен администратором",
            timestamp=now - timedelta(minutes=10)
        )
    ])
    requests.append(req5)

    session.flush()
    print(f" Создано {len(requests)} запросов по сценариям из ТЗ")
    return requests


def init_database():
    """Основная функция инициализации БД"""
    print("️  Инициализация базы данных NEO Approvements...")
    print("=" * 60)

    # Создаем все таблицы
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(" Таблицы созданы\n")

    # Создаем сессию
    with SessionLocal() as session:
        try:
            # Создаем данные
            users = create_users(session)
            projects = create_projects(session, users)
            types = create_request_types(session)
            create_requests_scenarios(session, users, projects, types)

            session.commit()

            print("\n" + "=" * 60)
            print(" База данных успешно инициализирована!")
            print("=" * 60)
            print("\n Пользователи для входа:")
            print("   • pbasmanov / 123456 (Сотрудник)")
            print("   • adeev / 123456 (Руководитель)")
            print("   • avasulich / 123456 (Менеджер проекта)")
            print("   • divanovich / 123456 (Менеджер проекта)")
            print("   • ipetrovich / 123456 (Менеджер проекта)")
            print("   • agavrilich / 123456 (Менеджер проекта)")
            print("   • admin / admin (Администратор)")
            print("\n Созданные сценарии:")
            print("   1. req_001 - Отпуск pbasmanov (СОГЛАСОВАН)")
            print("   2. req_002 - Бюджет Проекта X (ОЖИДАЕТ единогласно)")
            print("   3. req_003 - Отпуск pbasmanov (ОТКЛОНЕН с причиной)")
            print("   4. req_004 - Бюджет Проекта Y (СОГЛАСОВАН, 1 голос)")
            print("   5. req_005 - Проект Z (АДМИНСКИЙ БЭКДОР)")
            print("=" * 60)

        except Exception as e:
            session.rollback()
            print(f"\nОшибка при инициализации БД: {e}")
            raise
        finally:
            session.close()


if __name__ == "__main__":
    init_database()