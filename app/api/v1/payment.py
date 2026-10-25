from functools import lru_cache

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.payment import PaymentCreateResponse
from app.services.payment import PaymentService


router = APIRouter()


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService()


@router.post(
    "/premium",
    response_model=PaymentCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_premium_payment(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    payment_service: PaymentService = Depends(get_payment_service),
):
    return await payment_service.create_payment(
        db=db,
        user=current_user,
    )