from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Добавляем корневую папку проекта в sys.path, чтобы Alembic видел папку 'app'
# (Без этого он выдаст ModuleNotFoundError, когда попытается импортировать твои модели)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

# 3. Импортируем Base из твоего database.py
from app.core.database import Base

# 4. ИМПОРТИРУЕМ ВСЕ МОДЕЛИ, чтобы Alembic их увидел и создал таблицы!
# ВАЖНО: Если ты создал новые модели, не забудь добавить их сюда!
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


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 5. Берем DATABASE_URL из .env и подсовываем его Alembic
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 6. Указываем метаданные твоих моделей (раньше тут было None)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()