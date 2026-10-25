from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user
from app.schemas.sleep import SleepAnalyticsRead
from app.services.sleep_analytics_service import SleepAnalyticsService

router = APIRouter()


async def require_research_access(
    current_user=Depends(get_current_user),
):
    # Если в проекте уже есть проверка ролей,
    # лучше переиспользовать её вместо этой функции.
    role = getattr(current_user, "role", None)
    role = getattr(role, "value", role)

    if str(role).lower() not in {"admin", "researcher"}:
        raise HTTPException(
            status_code=403,
            detail="Недостаточно прав для просмотра аналитики исследования.",
        )

    return current_user


@router.get(
    "/sleep",
    response_model=SleepAnalyticsRead,
)
async def get_sleep_analytics(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_research_access),
):
    try:
        return await SleepAnalyticsService(db).get_analytics(
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc