from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.workout_day import WorkoutDay


class WorkoutDayRepository:
    
    def get_by_id(self, db: Session, day_id: int) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(WorkoutDay.id == day_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_active_by_program(self, db: Session, program_id: int) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .where(
                WorkoutDay.workout_program_id == program_id, # <--- Исправили!
                WorkoutDay.is_archived.is_(False),
            )
            .order_by(WorkoutDay.day_order)
        )
        return db.execute(stmt).scalars().all()

    def get_archived_by_program(self, db: Session, program_id: int) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .where(
                WorkoutDay.workout_program_id == program_id, # <--- Исправили!
                WorkoutDay.is_archived.is_(True),
            )
            .order_by(WorkoutDay.day_order)
        )
        return db.execute(stmt).scalars().all()

    def get_by_order_and_program(self, db: Session, day_order: int, program_id: int) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(
            WorkoutDay.day_order == day_order,
            WorkoutDay.workout_program_id == program_id, # <--- Исправили!
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name_and_program(self, db: Session, name: str, program_id: int) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(
            WorkoutDay.name == name,
            WorkoutDay.workout_program_id == program_id, # <--- Исправили!
        )
        return db.execute(stmt).scalar_one_or_none()

    def search_by_name(self, db: Session, name: str) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .where(
                WorkoutDay.name.ilike(f"%{name}%"),
                WorkoutDay.is_archived.is_(False),
            )
            .order_by(WorkoutDay.day_order)
        )
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, day_db: WorkoutDay) -> WorkoutDay:
        db.add(day_db)
        return day_db

    def update(
        self,
        db: Session,
        day_db: WorkoutDay,
        update_data: dict,
    ) -> WorkoutDay:
        for key, value in update_data.items():
            setattr(day_db, key, value)

        return day_db

    def delete(self, db: Session, day_db: WorkoutDay) -> None:
        db.delete(day_db)

    def archive(self, db: Session, day_db: WorkoutDay) -> WorkoutDay:
        day_db.is_archived = True
        return day_db

    def unarchive(self, db: Session, day_db: WorkoutDay) -> WorkoutDay:
        day_db.is_archived = False
        return day_db