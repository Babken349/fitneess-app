from fastapi import HTTPException, status
from app.models.users import User
from app.schemas.exercise import ExerciseUpdate, ExerciseCreate
from app.core.enums import UserRole
from sqlalchemy.orm import Session

from app.models import Exercise
from app.schemas import ExerciseCreate
from app.repository.exercise import ExerciseRepository, EquipmentRepository, MuscleGroupRepository

class ExerciseService:
    def __init__(self):
        self.exercise_repo = ExerciseRepository()
        self.muscle_group_repo = MuscleGroupRepository()
        self.equipment_repo = EquipmentRepository()

    def create_exercise(self, db: Session, exercise_data: ExerciseCreate, current_user: User) -> Exercise:

        # 1) Проверка прав
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You go not have permission to create exercises."
            )

        # 2) Проверка дублей имени
        existing_exercise = self.exercise_repo.get_by_name(db, exercise_data.name)
        if existing_exercise:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise with this name already exists."
            )

        # 3) Проверка группы мышц
        if exercise_data.muscle_group_id:
            muscle_group = self.muscle_group_repo.get_by_id(db, exercise_data.muscle_group_id)
            if not muscle_group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Muscle group not found."
                )

        # 4) Проверка оборудования
        if exercise_data.equipment_id:
            equipment = self.equipment_repo.get_by_id(db, exercise_data.equipment_id)
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Equipment not found."
                )
        exercise_db = Exercise(
            name=exercise_data.name,
            description=exercise_data.description,
            muscle_group_id=exercise_data.muscle_group_id,
            equipment_id=exercise_data.equipment_id
        )
        # 5) Вызов Репозитория для создания объекта (без commit)
        new_exercise = self.exercise_repo.create(db, exercise_db)
        # 6) Сохранение в БД (Транзакцией управляет Сервис)
        db.commit()
        db.refresh(new_exercise)

        return new_exercise



    def get_exercise_by_id(self, db, exercise_id):

        exercise = self.exercise_repo.get_by_id(db, exercise_id)

        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found."
            )
        return exercise

    def get_equipment_by_id(self, db, equipment_id):

        equipment = self.equipment_repo.get_by_id(db, equipment_id)

        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found."
            )
        return equipment


    def get_all_exercises(self, db: Session, skip: int = 0, limit: int = 20):
        return self.exercise_repo.get_all(db, skip=skip, limit=limit)

    def update_exercise(self, db: Session, exercise_id: int, exercise_data: ExerciseUpdate, current_user: User) -> Exercise:
        # 1) Проверка прав
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You go not have permission to create exercises."
            )

        exercise_db = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found."
            )

        if exercise_data.muscle_group_id is not None and exercise_data.muscle_group_id != exercise_db.muscle_group_id:
            muscle_group = self.muscle_group_repo.get_muscle_group_by_id(db, exercise_data.muscle_group_id)
            if not muscle_group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Muscle group not found."
                )
        if exercise_data.equipment_id is not None and exercise_data.equipment_id != exercise_db.equipment_id:
            if not self.equipment_repo.get_by_id(db, exercise_data.equipment_id):
                raise HTTPException(status_code=404, detail="Equipment not found.")

        exercise_updated = self.exercise_repo.update(db, exercise_data=exercise_data, exercise_db=exercise_db)

        db.commit()
        db.refresh(exercise_updated)

        return exercise_updated

    def delete_exercise(self, db: Session, exercise_id: int, current_user: User) -> None:
        # 1) Проверка прав
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You go not have permission to delete exercises."
            )

        exercise_db = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found."
            )

        self.exercise_repo.delete(db, exercise_db=exercise_db)
        db.commit()

    def archive_exercise(self, db: Session, exercise_id: int, current_user: User) -> Exercise:
        # 1) Проверка прав
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You go not have permission to delete exercises."
            )

        exercise_db = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found."
            )

        exercise_archived = self.exercise_repo.archive(db, exercise_db=exercise_db)
        db.commit()
        db.refresh(exercise_archived)

        return exercise_archived