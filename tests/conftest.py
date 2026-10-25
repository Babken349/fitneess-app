import asyncio
import os

import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
import uuid

from app.auth.security import create_access_token
from app.core.enums import UserRole
from app.models.achievement import Achievement
from app.models.users import User
from app.utils.password import password_manager
import app.models  # noqa: E402,F401
from app.main import app  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core.dependency import get_db  # noqa: E402
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent   # папка fitness/
load_dotenv(ROOT / ".env")        # нужен DATABASE_URL для защитной проверки
load_dotenv(ROOT / ".env.test", override=True)   # TEST_DATABASE_URL

TEST_URL = os.getenv("TEST_DATABASE_URL")

# Защита: drop_all разрушителен, поэтому проверяем всё до импорта приложения
if not TEST_URL:
    pytest.exit("Не задан TEST_DATABASE_URL (в .env или в окружении)", returncode=2)
if not TEST_URL.rsplit("/", 1)[-1].endswith("_test"):
    pytest.exit("Тесты разрешены только на базе с именем *_test", returncode=2)
if TEST_URL == os.getenv("DATABASE_URL"):
    pytest.exit("TEST_DATABASE_URL совпадает с DATABASE_URL", returncode=2)



def _run_ddl(drop_only: bool = False):
    async def go(): # run_ddl синхронная, нужна еще одна обертка для асинхронного вызова
        engine = create_async_engine(TEST_URL, poolclass=NullPool)
        async with engine.begin() as conn: #   открывает соединение с БД и автоматически начинает транзакцию
            await conn.run_sync(Base.metadata.drop_all)
            if not drop_only: #  переводится как только удалить таблицы, без создания новых, если true то пропускаем, false создаем новые таблицы.
                await conn.run_sync(Base.metadata.create_all) # синхронный метод, поэтому run_sync
        await engine.dispose() #  закрывает соединение с БД и освобождает ресурсы

    asyncio.run(go()) #  запускает асинхронную функцию go() в синхронном контексте


@pytest.fixture(scope="session") #  scope="session" означает, что фикстура будет выполняться один раз за сессию тестирования, а не для каждого теста.
def prepare_db():
    _run_ddl()                 # чистая схема в начале прогона
    yield
    _run_ddl(drop_only=True)   # убираем за собой таблицы в конце прогона


@pytest_asyncio.fixture
async def session(prepare_db):
    engine = create_async_engine(TEST_URL, poolclass=NullPool) #  poolclass=NullPool означает, что соединения не будут кэшироваться и будут закрываться после использования, что полезно для тестов, чтобы избежать проблем с повторным использованием соединений.
    async with engine.connect() as conn:  #  engine.connect() открывает соединение с базой данных, которое будет использоваться для выполнения операций в рамках фикстуры.
        outer = await conn.begin()  # conn.begin() начинает транзакцию на уровне соединения, которая будет использоваться для всех операций в рамках фикстуры. Это позволяет откатывать все изменения после завершения теста.
        s = AsyncSession(
            bind=conn,  #  bind=conn означает, что сессия будет использовать это соединение для выполнения всех операций с базой данных.
            expire_on_commit=False,  #  expire_on_commit=False означает, что объекты не будут истекать после коммита, что полезно для тестов.
            join_transaction_mode="create_savepoint",  #  join_transaction_mode="create_savepoint" означает, что при начале новой транзакции будет создана точка сохранения (savepoint), что позволяет откатывать изменения до этой точки без завершения всей транзакции.
        )
        try:
            yield s
        finally:
            await s.close()
            await outer.rollback()  #  откатывает все изменения, сделанные в рамках транзакции, чтобы база данных оставалась в исходном состоянии для следующих тестов.
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):

    async def override():
        yield session

    app.dependency_overrides[get_db] = override

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


TEST_PASSWORD = "Tractor-Blue-42x"
_password_hash_cache: str | None = None


async def _password_hash() -> str:
    # Хеширование намеренно медленное: считаем один раз за прогон
    global _password_hash_cache

    if _password_hash_cache is None:
        _password_hash_cache = await password_manager.hash(TEST_PASSWORD)

    return _password_hash_cache


@pytest_asyncio.fixture
async def make_user(session):
    async def factory(**overrides) -> User:
        uid = uuid.uuid4().hex[:8]
        data = {
            "login": f"user_{uid}",
            "email": f"user_{uid}@example.com",
            "hashed_password": await _password_hash(),
        }
        data.update(overrides)
        user = User(**data)
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    return factory


@pytest_asyncio.fixture
async def admin(make_user) -> User:
    return await make_user(role=UserRole.ADMIN.value)


@pytest.fixture
def auth_headers():
    def build(user: User) -> dict[str, str]:
        token = create_access_token(user_id=user.id, role=user.role)
        return {"Authorization": f"Bearer {token}"}

    return build


@pytest_asyncio.fixture
async def make_achievement(session):
    async def factory(**overrides) -> Achievement:
        uid = uuid.uuid4().hex[:8]
        data = {"name": f"Достижение {uid}", "code": f"code_{uid}"}
        data.update(overrides)
        achievement = Achievement(**data)
        session.add(achievement)
        await session.flush()
        await session.refresh(achievement)
        return achievement

    return factory

# =========================================================
# Workout / Exercise fixtures (для exercise_log и других)
# =========================================================

from app.models.exercise import Exercise              # noqa: E402
from app.models.workout_session import WorkoutSession  # noqa: E402


@pytest_asyncio.fixture
async def make_exercise(session):
    async def factory(**overrides) -> Exercise:
        uid = uuid.uuid4().hex[:8]
        data = {"name": f"Упражнение {uid}"}
        data.update(overrides)
        exercise = Exercise(**data)
        session.add(exercise)
        await session.flush()
        await session.refresh(exercise)
        return exercise

    return factory


@pytest_asyncio.fixture
async def make_workout_session(session):
    async def factory(*, user, **overrides) -> WorkoutSession:
        data = {
            "user_id": user.id,
            "workout_day_id": None,
        }
        data.update(overrides)
        ws = WorkoutSession(**data)
        session.add(ws)
        await session.flush()
        await session.refresh(ws)
        return ws

    return factory



# =========================================================
# MuscleGroup / Equipment fixtures
# =========================================================

from app.models.exercise import MuscleGroup, Equipment  # noqa: E402


@pytest_asyncio.fixture
async def make_muscle_group(session):
    async def factory(**overrides) -> MuscleGroup:
        uid = uuid.uuid4().hex[:8]
        data = {"name": f"Группа {uid}"}
        data.update(overrides)
        mg = MuscleGroup(**data)
        session.add(mg)
        await session.flush()
        await session.refresh(mg)
        return mg

    return factory


@pytest_asyncio.fixture
async def make_equipment(session):
    async def factory(**overrides) -> Equipment:
        uid = uuid.uuid4().hex[:8]
        data = {"name": f"Оборудование {uid}"}
        data.update(overrides)
        eq = Equipment(**data)
        session.add(eq)
        await session.flush()
        await session.refresh(eq)
        return eq

    return factory

# =========================================================
# Friendship fixture
# =========================================================

from app.models.friendship import Friendship  # noqa: E402


@pytest_asyncio.fixture
async def make_friendship(session):
    async def factory(*, requester, addressee, status="pending"):
        f = Friendship(
            requester_id=requester.id,
            addressee_id=addressee.id,
            status=status,
        )
        session.add(f)
        await session.flush()
        await session.refresh(f)
        return f

    return factory


# =========================================================
# Research / sleep / study fixtures
# =========================================================

from datetime import datetime, time          # noqa: E402

from app.models.sleep import SleepEntry                                # noqa: E402
from app.models.study_state import StudyState                          # noqa: E402
from app.models.study_test_result import StudyTestResult               # noqa: E402


@pytest_asyncio.fixture
async def make_sleep_entry(session):
    async def factory(*, user, sleep_date, duration_minutes=480):
        entry = SleepEntry(
            user_id=user.id,
            sleep_date=sleep_date,
            bedtime=time(23, 0),
            wake_time=time(7, 0),
            duration_minutes=duration_minutes,
        )
        session.add(entry)
        await session.flush()
        await session.refresh(entry)
        return entry

    return factory


@pytest_asyncio.fixture
async def make_study_state(session):
    async def factory(
        *,
        user,
        recorded_at,
        concentration=3,
        energy=3,
        fatigue=3,
        motivation=3,
    ):
        state = StudyState(
            user_id=user.id,
            recorded_at=recorded_at,
            concentration=concentration,
            energy=energy,
            fatigue=fatigue,
            motivation=motivation,
        )
        session.add(state)
        await session.flush()
        await session.refresh(state)
        return state

    return factory


@pytest_asyncio.fixture
async def make_study_test_result(session):
    async def factory(
        *,
        user,
        tested_at,
        score=80,
        max_score=100,
        exam_type="exam",
        subject="math",
    ):
        result = StudyTestResult(
            user_id=user.id,
            exam_type=exam_type,
            subject=subject,
            score=score,
            max_score=max_score,
            tested_at=tested_at,
        )
        session.add(result)
        await session.flush()
        await session.refresh(result)
        return result

    return factory


@pytest_asyncio.fixture
async def setup_exercise_log(
    client, make_user, make_exercise, make_workout_session, auth_headers
):
    """Возвращает (user, exercise_log_dict). Готовит всю цепочку через API."""
    async def factory():
        user = await make_user()
        exercise = await make_exercise()
        session = await make_workout_session(user=user)
        r = await client.post(
            f"/api/v1/workout-sessions/{session.id}/exercises",
            json={"exercise_id": exercise.id, "exercise_order": 1},
            headers=auth_headers(user),
        )
        assert r.status_code == 201, r.text
        return user, r.json()

    return factory