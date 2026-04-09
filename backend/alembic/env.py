from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ====================== ИМПОРТЫ ДЛЯ НАШЕГО ПРОЕКТА ======================
from app.config import settings
from app.models import Base

# ======================================================================

# Alembic Config object
config = context.config

# Подключаем URL базы из твоих settings
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ====================== САМОЕ ВАЖНОЕ ======================
# Указываем Alembic, где лежат наши модели
target_metadata = Base.metadata
# =========================================================

def run_migrations_offline() -> None:
    """Запуск в offline-режиме (для генерации SQL-скриптов)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск в online-режиме (обычный режим)"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()