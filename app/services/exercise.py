from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Exercise
from app.schemas import ExerciseCreate
from app.repository.exercise_repository import ExerciseRepository
from app.repository.muscle_group_repository import MuscleGroupRepository
from app.repository.equipment_repository import EquipmentRepository

class ExerciseService:
    # В конструктор мы передаем (инжектим) нужные репозитории.
    # Это позволяет легко подменять их в тестах.
    def __init__(self):
        self.exercise_repo = ExerciseRepository()
        self.muscle_group_repo = MuscleGroupRepository()
        self.equipment_repo = EquipmentRepository()

    def create_exercise(self, db: Session, exercise_data: ExerciseCreate, is_admin: bool) -> Exercise:
        """
        Создает упражнение. 
        Бизнес-логика:
        1. Только админ может создавать.
        2. Не должно быть дублей по имени.
        3. Группа мышц и оборудование должны существовать в БД.
        """
        # 1. Проверка прав
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create exercises."
            )

        # 2. Проверка дублей (используем точный поиск)
        existing_exercise = self.exercise_repo.get_by_name(db, exercise_data.name)
        if existing_exercise:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise with this name already exists."
            )

        # 3. Проверка группы мышц
        if exercise_data.muscle_group_id:
            muscle_group = self.muscle_group_repo.get_by_id(db, exercise_data.muscle_group_id)
            if not muscle_group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Muscle group not found."
                )

        # 4. Проверка оборудования
        if exercise_data.equipment_id:
            equipment = self.equipment_repo.get_by_id(db, exercise_data.equipment_id)
            if not equipment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Equipment not found."
                )

        # 5. Вызов Репозитория для создания объекта (без commit)
        new_exercise = self.exercise_repo.create(db, exercise_data)

        # 6. Сохранение в БД (Транзакцией управляет Сервис)
        db.commit()
        db.refresh(new_exercise)

        return new_exercise