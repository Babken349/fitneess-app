from unittest import skip

from sqlalchemy.orm import Session
from app.models.workout_program import WorkoutProgram
from sqlalchemy import select

class WorkoutProgramRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, program_id: int) -> WorkoutProgram | None:
        stmt = select(WorkoutProgram).where(WorkoutProgram.id == program_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_public(self, db: Session, skip: int, limit: int) -> list[WorkoutProgram]:
        stmt = select(WorkoutProgram).where(WorkoutProgram.is_public.is_(True)).offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()

    def search_by_name(self, db: Session, name: str) -> list[WorkoutProgram]:
        stmt = select(WorkoutProgram).where(WorkoutProgram.name.ilike(f"%{name}%"), WorkoutProgram.is_archived.is_(False))
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, program_db: WorkoutProgram) -> WorkoutProgram:
        db.add(program_db)
        return program_db

    def update(self, db: Session, program_db: WorkoutProgram) -> WorkoutProgram:
        return program_db

    def delete(self, db: Session, program_db: WorkoutProgram) -> None:
        db.delete(program_db)


    def get_active(self, db: Session) -> list[WorkoutProgram]:
        stmt = select(WorkoutProgram).where(
            WorkoutProgram.is_archived.is_(False)
        )

        return db.execute(stmt).scalars().all()

    def get_archived(self, db: Session) -> list[WorkoutProgram]:
        stmt = select(WorkoutProgram).where(
            WorkoutProgram.is_archived.is_(True)
        )

        return db.execute(stmt).scalars().all()
    
    def get_by_user(
    self,
    db: Session,
    user_id: int,
    skip: int = 0, 
    limit: int = 20,
    ) -> list[WorkoutProgram]:
        stmt = select(WorkoutProgram).where(
        WorkoutProgram.user_id == user_id
        ).offset(skip).limit(limit)

        return db.execute(stmt).scalars().all()


    def get_by_name_and_user(self, db: Session, name: str, user_id: int) -> WorkoutProgram | None:
        stmt = select(WorkoutProgram).where(
            WorkoutProgram.name == name,
            WorkoutProgram.user_id == user_id
        )
        return db.execute(stmt).scalar_one_or_none()

