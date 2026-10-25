
import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config


# Добавляем корень проекта в sys.path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

# Загружаем переменные окружения
load_dotenv()

# Импортируем Base и модели
from app.core.database import Base

from app.models.users import User
from app.models.exercise import Exercise
from app.models.workout_program import WorkoutProgram
from app.models.workout_day import WorkoutDay
from app.models.workout_exercise import WorkoutExercise
from app.models.workout_session import WorkoutSession
from app.models.body_weight import BodyWeight
from app.models.user_supplements import UserSupplement
from app.models.supplements import Supplement
from app.models.reminder import Reminder
from app.models.achievement import Achievement


# Конфигурация Alembic
config = context.config

# Получаем URL подключения из .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL не найден в .env")

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций без подключения к БД."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Выполнение миграций через синхронный интерфейс Alembic."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создание асинхронного подключения к БД."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций с асинхронным подключением."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()