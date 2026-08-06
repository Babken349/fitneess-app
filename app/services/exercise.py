from http.client import HTTPException

from sqlalchemy.orm import Session

from app.models import Exercise
from app.schemas.exercise import ExerciseUpdate, ExerciseCreate
from app.repository.exercise import ExerciseRepository, EquipmentRepository, MuscleGroupRepository
from app.exceptions import (
    ExerciseNotFoundError,
    ExerciseAlreadyExistsError,
    MuscleGroupNotFoundError,
    EquipmentNotFoundError
)

class ExerciseService:
    def __init__(self):
        self.exercise_repo = ExerciseRepository()
        self.muscle_group_repo = MuscleGroupRepository()
        self.equipment_repo = EquipmentRepository()

    def create_exercise(self, db: Session, exercise_data: ExerciseCreate) -> Exercise:
        # 1) Проверка дублей имени
        if self.exercise_repo.get_by_name(db, exercise_data.name):
            raise ExerciseAlreadyExistsError(exercise_data.name)

        # 2) Проверка группы мышц
        if exercise_data.muscle_group_id is not None:
            if not self.muscle_group_repo.get_by_id(db, exercise_data.muscle_group_id):
                raise MuscleGroupNotFoundError(exercise_data.muscle_group_id)

        # 3) Проверка оборудования
        if exercise_data.equipment_id is not None:
            if not self.equipment_repo.get_by_id(db, exercise_data.equipment_id):
                raise EquipmentNotFoundError(exercise_data.equipment_id)

        # 4) Создание объекта и сохранение
        exercise_db = Exercise(**exercise_data.model_dump())
        new_exercise = self.exercise_repo.create(db, exercise_db)
        
        db.commit()
        db.refresh(new_exercise)

        return new_exercise

    def get_exercise_by_id(self, db: Session, exercise_id: int) -> Exercise:
        exercise = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise:
            raise ExerciseNotFoundError(exercise_id)
        return exercise

    def get_all_exercises(self, db: Session, skip: int = 0, limit: int = 20) -> list[Exercise]:
        return self.exercise_repo.get_all(db, skip=skip, limit=limit)

    def search_exercises(self, db: Session, name_substring: str) -> list[Exercise]:
        # Вызываем метод поиска из репозитория
        return self.exercise_repo.search_by_name(db, name_substring)

    def update_exercise(self, db: Session, exercise_id: int, exercise_data: ExerciseUpdate) -> Exercise:
        # 1) Находим упражнение
        exercise_db = self.get_exercise_by_id(db, exercise_id)

        # 2) Берем только переданные поля
        update_data = exercise_data.model_dump(exclude_unset=True)

        # 3) Проверка дубликата имени
        if "name" in update_data and update_data["name"] != exercise_db.name:
            if self.exercise_repo.get_by_name(db, update_data["name"]):
                # Используем доменную ошибку, а не HTTPException!
                raise ExerciseAlreadyExistsError(update_data["name"])

        # 4) Проверяем новые Foreign Keys, если их передали
        if "muscle_group_id" in update_data and update_data["muscle_group_id"] != exercise_db.muscle_group_id:
            if not self.muscle_group_repo.get_by_id(db, update_data["muscle_group_id"]):
                raise MuscleGroupNotFoundError(update_data["muscle_group_id"])

        if "equipment_id" in update_data and update_data["equipment_id"] != exercise_db.equipment_id:
            if not self.equipment_repo.get_by_id(db, update_data["equipment_id"]):
                raise EquipmentNotFoundError(update_data["equipment_id"])

        # 5) Обновляем атрибуты
        for key, value in update_data.items():
            setattr(exercise_db, key, value)

        # 6) Сохраняем
        db.commit()
        db.refresh(exercise_db)

        return exercise_db

    def delete_exercise(self, db: Session, exercise_id: int) -> None:
        exercise_db = self.get_exercise_by_id(db, exercise_id)
        self.exercise_repo.delete(db, exercise_db=exercise_db)
        db.commit()

    def archive_exercise(self, db: Session, exercise_id: int) -> Exercise:
        exercise_db = self.get_exercise_by_id(db, exercise_id)
        self.exercise_repo.archive(db, exercise_db)

        db.commit()
        db.refresh(exercise_db)

        return exercise_db

def unarchive_exercise(self, db: Session, exercise_id: int) -> Exercise:
    exercise_db = self.get_exercise_by_id(db, exercise_id)

    exercise = self.exercise_repo.unarchive(db, exercise_db)

    db.commit()
    db.refresh(exercise)

    return exercise


def get_active_exercises(self, db: Session) -> list[Exercise]:
    return self.exercise_repo.get_active(db)


def get_archived_exercises(self, db: Session) -> list[Exercise]:
    return self.exercise_repo.get_archived(db)


def get_exercises_by_muscle_group(
    self,
    db: Session,
    muscle_group_id: int
) -> list[Exercise]:

    if not self.muscle_group_repo.get_by_id(db, muscle_group_id):
        raise MuscleGroupNotFoundError(muscle_group_id)

    return self.exercise_repo.get_by_muscle_group(db, muscle_group_id)


def get_exercises_by_equipment(
    self,
    db: Session,
    equipment_id: int
) -> list[Exercise]:

    if not self.equipment_repo.get_by_id(db, equipment_id):
        raise EquipmentNotFoundError(equipment_id)

    return self.exercise_repo.get_by_equipment(db, equipment_id)