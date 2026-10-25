from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import PaginatedResponse
from app.core.dependency import get_db
from app.auth.dependencies import get_current_user

from app.schemas.workout_program import (
    CreateWorkoutProgram,
    WorkoutProgramUpdate,
    WorkoutProgramResponse,
)
from app.models.users import User
from app.services.workout_program import ProgramService

router = APIRouter()

workout_program_service = ProgramService()


@router.post(
    "/workout-programs",
    response_model=WorkoutProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program(
    program_data: CreateWorkoutProgram,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.create_program(
        db=db,
        program_data=program_data,
        current_user=current_user,
    )


# =========================================================
# Конкретные пути ("me", "public", "search") должны стоять
# ДО "/workout-programs/{program_id}", иначе FastAPI попытается
# превратить слово в int и вернёт 422
# =========================================================

@router.get(
    "/workout-programs/me",
    response_model=PaginatedResponse[WorkoutProgramResponse],
)
async def get_my_programs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await workout_program_service.get_my_programs(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )
    return PaginatedResponse[WorkoutProgramResponse](
        items=[WorkoutProgramResponse.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )

# "/me/archived" и "/me/active" тоже ДО "/me/{program_id}"
@router.get(
    "/workout-programs/me/archived",
    response_model=list[WorkoutProgramResponse],
)
async def get_archived_by_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.get_archived_by_user(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/workout-programs/me/active",
    response_model=list[WorkoutProgramResponse],
)
async def get_active_by_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.get_active_by_user(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/workout-programs/me/{program_id}",
    response_model=WorkoutProgramResponse,
)
async def get_my_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.get_my_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get(
    "/workout-programs/public",
    response_model=PaginatedResponse[WorkoutProgramResponse],
)
async def get_public_programs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await workout_program_service.get_public_programs(
        db=db,
        skip=skip,
        limit=limit,
    )
    return PaginatedResponse[WorkoutProgramResponse](
        items=[WorkoutProgramResponse.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/workout-programs/search",
    response_model=list[WorkoutProgramResponse],
)
async def search_programs(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.search_programs(
        db=db,
        name=name,
        current_user=current_user,
    )


@router.get(
    "/workout-programs/{program_id}",
    response_model=WorkoutProgramResponse,
)
async def get_program_by_id(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.get_accessible_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch(
    "/workout-programs/{program_id}",
    response_model=WorkoutProgramResponse,
)
async def update_program(
    program_id: int,
    program_data: WorkoutProgramUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.update_program(
        db=db,
        program_id=program_id,
        program_data=program_data,
        current_user=current_user,
    )


@router.patch(
    "/workout-programs/{program_id}/archive",
    response_model=WorkoutProgramResponse,
)
async def archive_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.archive_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch(
    "/workout-programs/{program_id}/unarchive",
    response_model=WorkoutProgramResponse,
)
async def unarchive_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.unarchive_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch(
    "/workout-programs/{program_id}/public",
    response_model=WorkoutProgramResponse,
)
async def make_public(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.make_public(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch(
    "/workout-programs/{program_id}/private",
    response_model=WorkoutProgramResponse,
)
async def make_private(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await workout_program_service.make_private(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.delete(
    "/workout-programs/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await workout_program_service.delete_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )

    return None