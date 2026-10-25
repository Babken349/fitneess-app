from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.models.users import User
from app.schemas.study_test_result import (
    StudyTestResultCreate,
    StudyTestResultResponse,
)
from app.services.study_test_result import StudyTestResultService
from app.auth.dependencies import get_current_user


router = APIRouter()

study_test_result_service = StudyTestResultService()


@router.post(
    "",
    response_model=StudyTestResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_study_test_result(
    data: StudyTestResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_test_result_service.create(
        db,
        data,
        current_user,
    )


@router.get(
    "",
    response_model=list[StudyTestResultResponse],
)
async def get_my_test_results(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_test_result_service.get_my_results(
        db,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/{result_id}",
    response_model=StudyTestResultResponse,
)
async def get_study_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_test_result_service.get_by_id(
        db,
        result_id,
        current_user,
    )


@router.delete(
    "/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_study_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await study_test_result_service.delete(
        db,
        result_id,
        current_user,
    )