from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import require_admin
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
)

from app.services.exercise import ExerciseService


router = APIRouter()

exercise_service = ExerciseService()


# =========================
# CREATE
# =========================

@router.post(
    "",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await exercise_service.create_exercise(
        db=db,
        exercise_data=exercise_data,
    )


# =========================
# GET ALL
# =========================

@router.get(
    "",
    response_model=list[ExerciseResponse],
)
async def get_exercises(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_all(
        db=db,
        skip=skip,
        limit=limit,
    )


# =========================
# BY MUSCLE + EQUIPMENT
# Должен стоять ДО "/{exercise_id}", иначе "filter" попадёт в int-параметр
# =========================

@router.get(
    "/filter",
    response_model=list[ExerciseResponse],
)
async def get_exercises_by_filter(
    muscle_group_id: int,
    equipment_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_by_muscle_group_and_equipment(
        db=db,
        muscle_group_id=muscle_group_id,
        equipment_id=equipment_id,
        skip=skip,
        limit=limit,
    )


# =========================
# GET BY ID
# =========================

@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
async def get_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_by_id(
        db=db,
        exercise_id=exercise_id,
    )


# =========================
# UPDATE
# =========================

@router.patch(
    "/{exercise_id}",
    response_model=ExerciseResponse,
)
async def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await exercise_service.update_exercise(
        db=db,
        exercise_id=exercise_id,
        exercise_data=exercise_data,
    )


# =========================
# DELETE
# =========================

@router.delete(
    "/{exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await exercise_service.delete_exercise(
        db=db,
        exercise_id=exercise_id,
    )

    return None


# =========================
# ARCHIVE
# =========================

@router.patch(
    "/{exercise_id}/archive",
    response_model=ExerciseResponse,
)
async def archive_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await exercise_service.archive_exercise(
        db=db,
        exercise_id=exercise_id,
    )


# =========================
# UNARCHIVE
# =========================

@router.patch(
    "/{exercise_id}/unarchive",
    response_model=ExerciseResponse,
)
async def unarchive_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await exercise_service.unarchive_exercise(
        db=db,
        exercise_id=exercise_id,
    )


# =========================
# ACTIVE
# =========================

@router.get(
    "/status/active",
    response_model=list[ExerciseResponse],
)
async def get_active_exercises(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_active(
        db=db,
        skip=skip,
        limit=limit,
    )


# =========================
# ARCHIVED
# =========================

@router.get(
    "/status/archived",
    response_model=list[ExerciseResponse],
)
async def get_archived_exercises(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_archived(
        db=db,
        skip=skip,
        limit=limit,
    )


# =========================
# BY MUSCLE GROUP
# =========================

@router.get(
    "/muscle-group/{muscle_group_id}",
    response_model=list[ExerciseResponse],
)
async def get_exercises_by_muscle_group(
    muscle_group_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_by_muscle_group(
        db=db,
        muscle_group_id=muscle_group_id,
        skip=skip,
        limit=limit,
    )


# =========================
# BY EQUIPMENT
# =========================

@router.get(
    "/equipment/{equipment_id}",
    response_model=list[ExerciseResponse],
)
async def get_exercises_by_equipment(
    equipment_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.get_by_equipment(
        db=db,
        equipment_id=equipment_id,
        skip=skip,
        limit=limit,
    )


# =========================
# SEARCH
# =========================

@router.get(
    "/search/name",
    response_model=list[ExerciseResponse],
)
async def search_exercises(
    name: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await exercise_service.search_by_name(
        db=db,
        name=name,
        skip=skip,
        limit=limit,
    )