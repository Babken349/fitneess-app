"""Seed для разработки: демо-аккаунты, справочник упражнений, программа «Базовая»
и данные за 14 дней для участника demo_athlete.

Запуск (из корня проекта, файл лежит в app/seed.py):
    docker compose exec backend python -m app.seed
    DATABASE_URL=postgresql+asyncpg://...@localhost:5432/mydb python -m app.seed

Скрипт можно запускать повторно: уже существующее не дублируется.
Только для локальной разработки, пароль демо-аккаунтов не для production.
"""
import asyncio
import os
import random
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select

import app.models  # noqa: F401  (регистрирует все модели)
from app.core.database import AsyncSessionLocal
from app.core.enums import UserRole
from app.models.exercise import Equipment, Exercise, MuscleGroup
from app.models.sleep import SleepEntry
from app.models.study_state import StudyState
from app.models.study_test_result import StudyTestResult
from app.models.users import User
from app.models.workout_day import WorkoutDay
from app.models.workout_exercise import WorkoutExercise
from app.models.workout_program import WorkoutProgram
from app.utils.password import password_manager

PASSWORD = os.getenv("SEED_PASSWORD", "DemoPass123!")

# Вход по логину или email. Роль не указана: берётся значение по умолчанию из модели.
USERS = [
    dict(login="demo_athlete", email="athlete@example.com", is_verified=True),
    dict(login="demo_empty", email="empty@example.com", is_verified=True),
    dict(login="demo_researcher", email="researcher@example.com", is_verified=True,
         role=UserRole.RESEARCHER),
    dict(login="demo_admin", email="admin@example.com", is_verified=True,
         role=UserRole.ADMIN),
    dict(login="demo_unverified", email="unverified@example.com", is_verified=False),
]

MUSCLES = ["Грудь", "Спина", "Ноги", "Плечи", "Руки", "Пресс"]
EQUIPMENT = ["Штанга", "Гантели", "Тренажёр", "Собственный вес"]

# (название, группа мышц, оборудование)
EXERCISES = [
    ("Жим штанги лёжа", "Грудь", "Штанга"),
    ("Жим гантелей сидя", "Плечи", "Гантели"),
    ("Разводка гантелей лёжа", "Грудь", "Гантели"),
    ("Отжимания на брусьях", "Грудь", "Собственный вес"),
    ("Тяга верхнего блока", "Спина", "Тренажёр"),
    ("Тяга штанги в наклоне", "Спина", "Штанга"),
    ("Подтягивания", "Спина", "Собственный вес"),
    ("Сгибание рук с гантелями", "Руки", "Гантели"),
    ("Приседания со штангой", "Ноги", "Штанга"),
    ("Жим ногами", "Ноги", "Тренажёр"),
    ("Румынская тяга", "Ноги", "Штанга"),
    ("Скручивания", "Пресс", "Собственный вес"),
]

PROGRAM_NAME = "Базовая"
PROGRAM_DESCRIPTION = "Три тренировки на всё тело для старта"
PROGRAM_DAYS = [
    ("Тренировка A", ["Жим штанги лёжа", "Жим гантелей сидя",
                      "Разводка гантелей лёжа", "Отжимания на брусьях"]),
    ("Тренировка B", ["Тяга верхнего блока", "Тяга штанги в наклоне",
                      "Подтягивания", "Сгибание рук с гантелями"]),
    ("Тренировка C", ["Приседания со штангой", "Жим ногами",
                      "Румынская тяга", "Скручивания"]),
]

SUBJECTS = ["Математика", "Физика", "Английский"]


def build(model, **values):
    """Создаёт объект модели. Неизвестные поля пропускает с предупреждением,
    а при нехватке обязательных останавливается с понятным сообщением."""
    columns = {c.key: c for c in model.__table__.columns}
    dropped = [k for k in values if k not in columns]
    if dropped:
        print(f"  ! {model.__name__}: нет полей {dropped}, пропущены")
    values = {k: v for k, v in values.items() if k in columns}
    missing = [
        c.key for c in columns.values()
        if not c.nullable and not c.primary_key
        and c.default is None and c.server_default is None
        and c.key not in values
    ]
    if missing:
        raise SystemExit(
            f"{model.__name__}: не заполнены обязательные поля {missing}. "
            f"Добавьте их в seed или пришлите файл модели."
        )
    return model(**values)


async def get_or_create_named(db, model, name, **extra):
    obj = (await db.execute(select(model).where(model.name == name))).scalar_one_or_none()
    if obj is None:
        obj = build(model, name=name, **extra)
        db.add(obj)
        await db.flush()
    return obj


async def seed_users(db):
    pw_hash = await password_manager.hash(PASSWORD)
    result = {}
    for spec in USERS:
        user = (await db.execute(
            select(User).where(User.login == spec["login"])
        )).scalar_one_or_none()
        if user is None:
            user = build(User, hashed_password=pw_hash, **spec)
            db.add(user)
            await db.flush()
            print(f"  + пользователь {spec['login']}")
        result[spec["login"]] = user
    return result


async def seed_catalogue(db):
    muscles = {n: await get_or_create_named(db, MuscleGroup, n) for n in MUSCLES}
    equipment = {n: await get_or_create_named(db, Equipment, n) for n in EQUIPMENT}
    exercises = {}
    for name, muscle, equip in EXERCISES:
        exercises[name] = await get_or_create_named(
            db, Exercise, name,
            muscle_group_id=muscles[muscle].id,
            equipment_id=equipment[equip].id,
            is_archived=False,
        )
    return exercises


async def seed_program(db, owner, exercises):
    program = (await db.execute(
        select(WorkoutProgram).where(
            WorkoutProgram.user_id == owner.id,
            WorkoutProgram.name == PROGRAM_NAME,
        )
    )).scalar_one_or_none()
    if program is not None:
        return
    program = build(
        WorkoutProgram, user_id=owner.id, name=PROGRAM_NAME,
        description=PROGRAM_DESCRIPTION, is_public=True, is_archived=False,
    )
    db.add(program)
    await db.flush()
    for day_order, (day_name, names) in enumerate(PROGRAM_DAYS, start=1):
        day = build(
            WorkoutDay, workout_program_id=program.id, name=day_name,
            day_order=day_order, is_archived=False,
        )
        db.add(day)
        await db.flush()
        for order, ex_name in enumerate(names, start=1):
            db.add(build(
                WorkoutExercise, workout_day_id=day.id,
                exercise_id=exercises[ex_name].id, exercise_order=order,
            ))
    await db.flush()
    print(f"  + программа «{PROGRAM_NAME}» ({len(PROGRAM_DAYS)} дня)")


async def seed_demo_data(db, user):
    """14 дней сна, подготовки и результатов тестов. Значения сгенерированы
    так, чтобы концентрация и оценки зависели от сна: корреляция на панели
    исследователя получается ненулевой. Шкалы 1–5 подходят и под вариант 1–5,
    и под вариант 1–10 (решение по E3)."""
    count = (await db.execute(
        select(func.count()).select_from(SleepEntry).where(SleepEntry.user_id == user.id)
    )).scalar_one()
    if count:
        return

    rng = random.Random(42)
    today = date.today()
    for i in range(14, 0, -1):
        wake_date = today - timedelta(days=i)  # sleep_date: дата пробуждения
        bed_minutes = rng.choice([22, 23, 23, 0]) * 60 + rng.choice([0, 15, 30, 45])
        duration = rng.randint(380, 520)
        wake_minutes = (bed_minutes + duration) % 1440
        db.add(build(
            SleepEntry, user_id=user.id, sleep_date=wake_date,
            bedtime=time(bed_minutes // 60 % 24, bed_minutes % 60),
            wake_time=time(wake_minutes // 60, wake_minutes % 60),
            duration_minutes=duration, note=None,
        ))

        quality = (duration - 380) / 140  # 0..1
        concentration = max(1, min(5, round(1 + quality * 3) + rng.choice([0, 0, 1])))
        db.add(build(
            StudyState, user_id=user.id,
            concentration=concentration,
            energy=max(1, min(5, round(1 + quality * 3) + rng.choice([0, 1]))),
            fatigue=max(1, min(5, round(5 - quality * 3) + rng.choice([0, 0, 1]))),
            motivation=rng.randint(2, 5),
            subject=rng.choice(SUBJECTS),
            duration_minutes=rng.choice([45, 60, 90, 120]),
            notes=None,
            recorded_at=datetime.combine(wake_date, time(18, 0)),
        ))

        if i % 3 == 0:
            score = max(0, min(100, round(55 + quality * 35 + rng.randint(-5, 5))))
            db.add(build(
                StudyTestResult, user_id=user.id, exam_type="Контрольная",
                subject=rng.choice(SUBJECTS), score=score, max_score=100,
                duration_minutes=45, notes=None,
                tested_at=datetime.combine(wake_date, time(12, 0)),
            ))
    await db.flush()
    print("  + данные за 14 дней для demo_athlete (сон, подготовка, тесты)")


async def main():
    async with AsyncSessionLocal() as db:
        print("Seed:")
        users = await seed_users(db)
        exercises = await seed_catalogue(db)
        await seed_program(db, users["demo_athlete"], exercises)
        await seed_demo_data(db, users["demo_athlete"])
        await db.commit()

    print("\nГотово. Демо-аккаунты (вход по логину или email):")
    for spec in USERS:
        print(f"  {spec['login']:<16} {spec['email']}")
    print(f"Пароль для всех: {PASSWORD}")
    print("Вес (body_weights) не заполнен: нужна модель app/models/body_weight.py.")


if __name__ == "__main__":
    asyncio.run(main())