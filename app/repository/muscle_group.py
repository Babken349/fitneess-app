from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.exercise import MuscleGroup


class MuscleGroupRepository:
    
    def get_by_id(self, db: Session, muscle_group_id: int) -> MuscleGroup | None:
        stmt = select(MuscleGroup).where(MuscleGroup.id == muscle_group_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> MuscleGroup | None:
        stmt = select(MuscleGroup).where(MuscleGroup.name == name)
        return db.execute(stmt).scalar_one_or_none()