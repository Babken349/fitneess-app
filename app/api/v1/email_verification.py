from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.email_verification import EmailVerificationResponse
from app.services.email_verification import EmailVerificationService

router = APIRouter()  # ← важно: без prefix

service = EmailVerificationService()


@router.post(
    "/send",
    response_model=EmailVerificationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_verification_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.send_verification_email(db, current_user)

    return EmailVerificationResponse(
        message="Verification email sent",
    )


@router.get(
    "/verify",
    response_model=EmailVerificationResponse,
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    await service.verify_email(db, token)

    return EmailVerificationResponse(
        message="Email successfully verified",
    )