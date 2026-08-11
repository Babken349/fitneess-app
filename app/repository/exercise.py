from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise


class ExerciseRepository:

    def get_by_id(
        self,
        db: Session,
        exercise_id: int,
    ) -> Exercise | None:
        stmt = select(Exercise).where(
            Exercise.id == exercise_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> Exercise | None:
        stmt = select(Exercise).where(
            Exercise.name == name
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_archived(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(True))
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_active(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_muscle_group(
        self,
        db: Session,
        muscle_group_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.muscle_group_id == muscle_group_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_equipment(
        self,
        db: Session,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.equipment_id == equipment_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_muscle_group_and_equipment(
        self,
        db: Session,
        muscle_group_id: int,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.muscle_group_id == muscle_group_id,
                Exercise.equipment_id == equipment_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def search_by_name(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.name.ilike(f"%{name}%"),
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def exists_by_name(
        self,
        db: Session,
        name: str,
    ) -> bool:
        stmt = select(Exercise).where(
            Exercise.name == name
        )

        return db.execute(stmt).scalar_one_or_none() is not None

    def create(
        self,
        db: Session,
        exercise_db: Exercise,
    ) -> Exercise:
        db.add(exercise_db)
        return exercise_db

    def update(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        return exercise_db

    def delete(
        self,
        db: Session,
        exercise_db: Exercise,
    ) -> None:
        db.delete(exercise_db)

    def archive(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        exercise_db.is_archived = True
        return exercise_db

    def unarchive(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        exercise_db.is_archived = False
        return exercise_db