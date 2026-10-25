from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.schemas.common import PaginatedResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user
from app.schemas.sleep import SleepCreate, SleepRead, SleepUpdate
from app.services.sleep_service import (
    InvalidSleepDurationError,
    SleepAlreadyExistsError,
    SleepNotFoundError,
    SleepService,
)

router = APIRouter()


@router.post(
    "/",
    response_model=SleepRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_sleep(
    payload: SleepCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = SleepService(db)

    try:
        return await service.create(
            user_id=current_user.id,
            payload=payload,
        )
    except SleepAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidSleepDurationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/", response_model=PaginatedResponse[SleepRead])
async def list_sleep(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = SleepService(db)
    try:
        items, total = await service.list_entries(
            user_id=current_user.id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PaginatedResponse[SleepRead](
        items=[SleepRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )

@router.get("/{sleep_id}", response_model=SleepRead)
async def get_sleep(
    sleep_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return await SleepService(db).get_one(sleep_id, current_user.id)
    except SleepNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{sleep_id}", response_model=SleepRead)
async def update_sleep(
    sleep_id: int,
    payload: SleepUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = SleepService(db)

    try:
        return await service.update(
            sleep_id=sleep_id,
            user_id=current_user.id,
            payload=payload,
        )
    except SleepNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidSleepDurationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete(
    "/{sleep_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sleep(
    sleep_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        await SleepService(db).delete(sleep_id, current_user.id)
    except SleepNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)