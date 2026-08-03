from sqlalchemy import select, and_
from sqlalchemy.orm import Session

# Импортируем и модель, и схему
from app.models import Exercise
from app.schemas import ExerciseCreate 

class ExerciseRepository:
    
    def get_by_id(self, db: Session, exercise_id: int) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_name(self, db: Session, exercise_name: str) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.name == exercise_name)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> list[Exercise]:
        # Только неархивированные
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        return result.scalars().all()

    def create(self, db: Session, exercise_data: ExerciseCreate) -> Exercise:
        # Правильное создание: распаковываем словарь из Pydantic-схемы
        new_exercise = Exercise(**exercise_data.model_dump())
        db.add(new_exercise)
        return new_exercise

    def search(self, db: Session, name: str) -> list[Exercise]:
        # Правильное использование and_ со скобками
        stmt = select(Exercise).where(
            and_(
                Exercise.name.ilike(f"%{name}%"),
                Exercise.is_archived.is_(False)
            )
        )
        result = db.execute(stmt)
        return result.scalars().all()

    def archive(self, db: Session, exercise: Exercise) -> Exercise:
        exercise.is_archived = True
        return exercise