from datetime import date, datetime, time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sleep import SleepEntry
from app.repository.sleep_repository import SleepRepository
from app.schemas.sleep import SleepCreate, SleepUpdate


class SleepNotFoundError(Exception):
    pass


class SleepAlreadyExistsError(Exception):
    pass


class InvalidSleepDurationError(Exception):
    pass


class SleepService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SleepRepository()

    @staticmethod
    def calculate_duration(
        bedtime: time,
        wake_time: time,
    ) -> int:
        if bedtime == wake_time:
            raise InvalidSleepDurationError(
                "Время засыпания и пробуждения не может совпадать."
            )

        start = datetime.combine(date.min, bedtime)
        end = datetime.combine(date.min, wake_time)

        seconds = (end - start).total_seconds()

        # Если пробуждение раньше времени засыпания,
        # значит сон пересёк полночь.
        if seconds < 0:
            seconds += 24 * 60 * 60

        duration_minutes = round(seconds / 60)

        if duration_minutes <= 0 or duration_minutes > 18 * 60:
            raise InvalidSleepDurationError(
                "Продолжительность сна должна быть от 1 минуты до 18 часов."
            )

        return duration_minutes

    async def create(
        self,
        user_id: int,
        payload: SleepCreate,
    ) -> SleepEntry:
        existing = await self.repository.get_by_date_for_user(
            self.db,
            sleep_date=payload.sleep_date,
            user_id=user_id,
        )

        if existing:
            raise SleepAlreadyExistsError(
                "Запись о сне за эту дату уже существует."
            )

        duration_minutes = self.calculate_duration(
            payload.bedtime,
            payload.wake_time,
        )

        entry = SleepEntry(
            user_id=user_id,
            sleep_date=payload.sleep_date,
            bedtime=payload.bedtime,
            wake_time=payload.wake_time,
            duration_minutes=duration_minutes,
            note=payload.note,
        )

        try:
            self.repository.create(self.db, entry)
            await self.db.commit()
            await self.db.refresh(entry)
        except IntegrityError as exc:
            await self.db.rollback()
            raise SleepAlreadyExistsError(
                "Запись о сне за эту дату уже существует."
            ) from exc

        return entry

    async def get_one(
        self,
        sleep_id: int,
        user_id: int,
    ) -> SleepEntry:
        entry = await self.repository.get_by_id_for_user(
            self.db,
            sleep_id=sleep_id,
            user_id=user_id,
        )

        if entry is None:
            raise SleepNotFoundError("Запись о сне не найдена.")

        return entry

    async def list_entries(
        self,
        user_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[SleepEntry], int]:
        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from не может быть позже date_to.")

        items = await self.repository.list_for_user(
            self.db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )
        total = await self.repository.count_for_user(
            self.db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
        return items, total

    async def update(
        self,
        sleep_id: int,
        user_id: int,
        payload: SleepUpdate,
    ) -> SleepEntry:
        entry = await self.get_one(sleep_id, user_id)

        # Меняем только те поля, которые пришли в PATCH.
        changes = payload.model_dump(exclude_unset=True)

        bedtime = changes.get("bedtime", entry.bedtime)
        wake_time = changes.get("wake_time", entry.wake_time)

        if bedtime is None or wake_time is None:
            raise InvalidSleepDurationError(
                "Время засыпания и пробуждения обязательны."
            )

        duration_minutes = self.calculate_duration(
            bedtime,
            wake_time,
        )

        entry.bedtime = bedtime
        entry.wake_time = wake_time
        entry.duration_minutes = duration_minutes

        if "note" in changes:
            entry.note = changes["note"]

        try:
            await self.db.commit()
            await self.db.refresh(entry)
        except IntegrityError:
            await self.db.rollback()
            raise

        return entry

    async def delete(
        self,
        sleep_id: int,
        user_id: int,
    ) -> None:
        entry = await self.get_one(sleep_id, user_id)
        await self.repository.delete(self.db, entry)
        await self.db.commit()