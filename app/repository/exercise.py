from app.models.exercise import Equipment, Exercise, MuscleGroup
from sqlalchemy import select
from sqlalchemy.orm import Session


class ExerciseRepository:
    def get_by_id(self, db:Session, exercise_id: int) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        result = db.execute(stmt).scalar_one_or_none()
        return result

    def get_by_name(self, db:Session, name: str) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.name == name)
        result = db.execute(stmt).scalar_one_or_none()
        return result

    def create(self, db:Session, exercise_data: Exercise) -> Exercise:
        db.add(exercise_data)
        
        return exercise_data

    def update(self, db:Session, exercise_db: Exercise, exercise_data: Exercise) -> Exercise:
        exercise_db.name = exercise_data.name
        exercise_db.description = exercise_data.description
        exercise_db.muscle_group_id = exercise_data.muscle_group_id
        exercise_db.equipment_id = exercise_data.equipment_id
        
        return exercise_db

    def delete(self, db:Session, exercise_db: Exercise) -> None:
        db.delete(exercise_db)
          

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> list[Exercise]:
        stmt = select(Exercise).offset(skip).limit(limit)
        result = db.execute(stmt).scalars().all()
        return result

    def get_by_muscle_group(self, db:Session, muscle_group: str) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.muscle_group == muscle_group)
        result = db.execute(stmt).scalars().all()
        return result

    def get_by_equipment(self, db:Session, equipment_id: int) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.equipment_id == equipment_id)
        result = db.execute(stmt).scalars().all()
        return result

    def get_archived(self, db:Session) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.is_archived.is_(True))
        result = db.execute(stmt).scalars().all()
        return result

    def get_active(self, db:Session) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.is_archived.is_(False))
        result = db.execute(stmt).scalars().all()
        return result

    def archive(self, db:Session, exercise_db: Exercise) -> Exercise:
        exercise_db.is_archived = True
        
        return exercise_db

    def unarchive(self, db:Session, exercise_db: Exercise) -> Exercise:
        exercise_db.is_archived = False
        
        return exercise_db


    def get_by_muscle_group_and_equipment(self, db:Session, muscle_group_id: int, equipment_id: int) -> list[Exercise]:
        stmt = select(Exercise).where(
            Exercise.muscle_group_id == muscle_group_id,
            Exercise.equipment_id == equipment_id
        )
        result = db.execute(stmt).scalars().all()
        return result



    def  search_by_name(self, db:Session, name_substring: str) -> list[Exercise]:
        stmt = select(Exercise).where(Exercise.name.ilike(f"%{name_substring}%"))
        result = db.execute(stmt).scalars().all()
        return result

    def exists_by_name(self, db: Session, name: str) -> bool:
        stmt = select(Exercise).where(Exercise.name == name)
        result = db.execute(stmt).scalar_one_or_none()
        return result is not None


class MuscleGroupRepository:
    def get_muscle_group_by_id(self, db:Session, muscle_group_id: int) -> MuscleGroup | None:
        stmt = select(MuscleGroup).where(MuscleGroup.id == muscle_group_id)
        result = db.execute(stmt).scalar_one_or_none()
        return result

class EquipmentRepository:
    def get_equipment_by_id(self, db:Session, equipment_id: int) -> Equipment | None:
        stmt = select(Equipment).where(Equipment.id == equipment_id)
        result = db.execute(stmt).scalar_one_or_none()
        return result