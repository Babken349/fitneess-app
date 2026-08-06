from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise, MuscleGroup, Equipment


class ExerciseRepository:

    def get_by_id(self, db: Session, exercise_id: int) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.name == name)
        return db.execute(stmt).scalar_one_or_none()

    def exists_by_name(self, db: Session, name: str) -> bool:
        stmt = select(Exercise).where(Exercise.name == name)
        return db.execute(stmt).scalar_one_or_none() is not None

    def create(self, db: Session, exercise_db: Exercise) -> Exercise:
        db.add(exercise_db)
        return exercise_db

    def update(self, db: Session, exercise_db: Exercise) -> Exercise:
        # SQLAlchemy уже отслеживает объект.
        # Сервис изменяет поля, репозиторий просто возвращает объект.
        return exercise_db

    def delete(self, db: Session, exercise_db: Exercise) -> None:
        db.delete(exercise_db)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> list[Exercise]:

        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_active(self, db: Session) -> list[Exercise]:
        stmt = select(Exercise).where(
            Exercise.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def get_archived(self, db: Session) -> list[Exercise]:
        stmt = select(Exercise).where(
            Exercise.is_archived.is_(True)
        )

        return db.execute(stmt).scalars().all()

    def get_by_muscle_group(
        self,
        db: Session,
        muscle_group_id: int
    ) -> list[Exercise]:

        stmt = select(Exercise).where(
            Exercise.muscle_group_id == muscle_group_id,
            Exercise.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def get_by_equipment(
        self,
        db: Session,
        equipment_id: int
    ) -> list[Exercise]:

        stmt = select(Exercise).where(
            Exercise.equipment_id == equipment_id,
            Exercise.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def get_by_muscle_group_and_equipment(
        self,
        db: Session,
        muscle_group_id: int,
        equipment_id: int
    ) -> list[Exercise]:

        stmt = select(Exercise).where(
            Exercise.muscle_group_id == muscle_group_id,
            Exercise.equipment_id == equipment_id,
            Exercise.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def search_by_name(
        self,
        db: Session,
        name_substring: str
    ) -> list[Exercise]:

        stmt = select(Exercise).where(
            Exercise.name.ilike(f"%{name_substring}%"),
            Exercise.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def archive(
        self,
        db: Session,
        exercise_db: Exercise
    ) -> Exercise:

        exercise_db.is_archived = True
        return exercise_db

    def unarchive(
        self,
        db: Session,
        exercise_db: Exercise
    ) -> Exercise:

        exercise_db.is_archived = False
        return exercise_db


class MuscleGroupRepository:

    def get_by_id(
        self,
        db: Session,
        muscle_group_id: int
    ) -> MuscleGroup | None:

        stmt = select(MuscleGroup).where(
            MuscleGroup.id == muscle_group_id
        )

        return db.execute(stmt).scalar_one_or_none()


class EquipmentRepository:

    def get_by_id(
        self,
        db: Session,
        equipment_id: int
    ) -> Equipment | None:

        stmt = select(Equipment).where(
            Equipment.id == equipment_id
        )

        return db.execute(stmt).scalar_one_or_none()