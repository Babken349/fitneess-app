from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.repository.exercise import ExerciseRepository
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate
from app.repository.muscle_group import MuscleGroupRepository
from app.repository.equipment import EquipmentRepository  
from app.exceptions import (
    ExerciseNotFoundError,
    ExerciseAlreadyExistsError,
    MuscleGroupNotFoundError,
    EquipmentNotFoundError,
)


class ExerciseService:

    def __init__(self):
        self.exercise_repo = ExerciseRepository()
        self.muscle_group_repo = MuscleGroupRepository()
        self.equipment_repo = EquipmentRepository()
    # =========================
    # CREATE
    # =========================

    def create_exercise(
        self,
        db: Session,
        exercise_data: ExerciseCreate,
    ) -> Exercise:

        if not exercise_data.name.strip():
            raise ValueError("Название упражнения не может быть пустым")

        if self.exercise_repo.exists_by_name(
            db,
            exercise_data.name,
        ):
            raise ExerciseAlreadyExistsError(
                exercise_data.name
            )

        muscle_group = self.muscle_group_repo.get_by_id(
            db,
            exercise_data.muscle_group_id,
        )
        if exercise_data.muscle_group_id is not None:
            if not muscle_group:
                raise MuscleGroupNotFoundError(
                    exercise_data.muscle_group_id
                )


        if exercise_data.equipment_id is not None:
            equipment = self.equipment_repo.get_equipment_by_id(
                db,
                exercise_data.equipment_id,
            )

            if not equipment:
                raise EquipmentNotFoundError(
                    exercise_data.equipment_id
                )

        exercise_db = Exercise(
            name=exercise_data.name,
            description=exercise_data.description,
            muscle_group_id=exercise_data.muscle_group_id,
            equipment_id=exercise_data.equipment_id,
        )

        self.exercise_repo.create(db, exercise_db)

        db.commit()
        db.refresh(exercise_db)

        return exercise_db

    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        db: Session,
        exercise_id: int,
    ) -> Exercise:

        exercise = self.exercise_repo.get_by_id(
            db,
            exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(exercise_id)

        return exercise

    # =========================
    # GET ALL
    # =========================

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        return self.exercise_repo.get_all(
            db,
            skip,
            limit,
        )

    # =========================
    # UPDATE
    # =========================

    def update_exercise(
        self,
        db: Session,
        exercise_id: int,
        exercise_data: ExerciseUpdate,
    ) -> Exercise:

        exercise = self.exercise_repo.get_by_id(
            db,
            exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(exercise_id)

        update_data = exercise_data.model_dump(
            exclude_unset=True
        )

        if "name" in update_data:

            if not update_data["name"].strip():
                raise ValueError(
                    "Название упражнения не может быть пустым"
                )

            existing = self.exercise_repo.get_by_name(
                db,
                update_data["name"],
            )

            if existing and existing.id != exercise_id:
                raise ExerciseAlreadyExistsError(
                    update_data["name"]
                )

        if "muscle_group_id" in update_data:

            muscle_group = self.muscle_group_repo.get_by_id(
                db,
                update_data["muscle_group_id"],
            )

            if not muscle_group:
                raise MuscleGroupNotFoundError(
                    update_data["muscle_group_id"]
                )

        if "equipment_id" in update_data:

            equipment = self.equipment_repo.get_equipment_by_id(
                db,
                update_data["equipment_id"],
            )

            if not equipment:
                raise EquipmentNotFoundError(
                    update_data["equipment_id"]
                )

        for key, value in update_data.items():
            setattr(exercise, key, value)

        self.exercise_repo.update(exercise)

        db.commit()
        db.refresh(exercise)

        return exercise

    # =========================
    # DELETE
    # =========================

    def delete_exercise(
        self,
        db: Session,
        exercise_id: int,
    ) -> None:

        exercise = self.exercise_repo.get_by_id(
            db,
            exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(exercise_id)

        self.exercise_repo.delete(
            db,
            exercise,
        )

        db.commit()

    # =========================
    # ARCHIVE
    # =========================

    def archive_exercise(
        self,
        db: Session,
        exercise_id: int,
    ) -> Exercise:

        exercise = self.exercise_repo.get_by_id(
            db,
            exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(exercise_id)

        self.exercise_repo.archive(exercise)

        db.commit()
        db.refresh(exercise)

        return exercise

    # =========================
    # UNARCHIVE
    # =========================

    def unarchive_exercise(
        self,
        db: Session,
        exercise_id: int,
    ) -> Exercise:

        exercise = self.exercise_repo.get_by_id(
            db,
            exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(exercise_id)

        self.exercise_repo.unarchive(exercise)

        db.commit()
        db.refresh(exercise)

        return exercise

    # =========================
    # ACTIVE
    # =========================

    def get_active(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        return self.exercise_repo.get_active(
            db,
            skip,
            limit,
        )

    # =========================
    # ARCHIVED
    # =========================

    def get_archived(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        return self.exercise_repo.get_archived(
            db,
            skip,
            limit,
        )

    # =========================
    # MUSCLE GROUP
    # =========================

    def get_by_muscle_group(
        self,
        db: Session,
        muscle_group_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        muscle_group = self.muscle_group_repo.get_by_id(
            db,
            muscle_group_id,
        )

        if not muscle_group:
            raise MuscleGroupNotFoundError(
                muscle_group_id
            )

        return self.exercise_repo.get_by_muscle_group(
            db,
            muscle_group_id,
            skip,
            limit,
        )

    # =========================
    # EQUIPMENT
    # =========================

    def get_by_equipment(
        self,
        db: Session,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        equipment = self.equipment_repo.get_equipment_by_id(
            db,
            equipment_id,
        )

        if not equipment:
            raise EquipmentNotFoundError(
                equipment_id
            )

        return self.exercise_repo.get_by_equipment(
            db,
            equipment_id,
            skip,
            limit,
        )

    # =========================
    # MUSCLE + EQUIPMENT
    # =========================

    def get_by_muscle_group_and_equipment(
        self,
        db: Session,
        muscle_group_id: int,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        muscle_group = self.muscle_group_repo.get_by_id(
            db,
            muscle_group_id,
        )

        if not muscle_group:
            raise MuscleGroupNotFoundError(
                muscle_group_id
            )

        equipment = self.equipment_repo.get_equipment_by_id(
            db,
            equipment_id,
        )

        if not equipment:
            raise EquipmentNotFoundError(
                equipment_id
            )

        return self.exercise_repo.get_by_muscle_group_and_equipment(
            db,
            muscle_group_id,
            equipment_id,
            skip,
            limit,
        )

    # =========================
    # SEARCH
    # =========================

    def search_by_name(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:

        return self.exercise_repo.search_by_name(
            db,
            name,
            skip,
            limit,
        )