from fastapi import APIRouter, Depends

from app.auth.dependencies import require_admin
from app.models.users import User
from app.services.email import EmailService


router = APIRouter()

email_service = EmailService()


@router.post("/test-email")
async def test_email(
    admin: User = Depends(require_admin),
):
    result = await email_service.send_email(
        to=admin.email,
        subject="Fitness App — тестовое письмо",
        html="""
        <h1>Привет!</h1>
        <p>Если ты видишь это письмо, Resend работает.</p>
        <p>Твоя почтовая система подключена к Fitness App.</p>
        """,
    )

    return {
        "message": "Email sent",
        "email": admin.email,
        "id": result.get("id") if isinstance(result, dict) else None,
    }