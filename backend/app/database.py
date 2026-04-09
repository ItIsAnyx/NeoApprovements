from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings
from backend.app.models import Base


DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_DATABASE}"
)

# =============================================
# ENGINE + SESSION
# =============================================
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =============================================
# Функция для создания таблиц (если нужно вручную)
# =============================================
def init_db() -> None:
    Base.metadata.create_all(bind=engine)


__all__ = ["engine", "SessionLocal", "Base", "init_db"]