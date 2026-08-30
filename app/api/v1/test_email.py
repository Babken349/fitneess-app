from fastapi import APIRouter, Depends


from app.auth.dependencies import get_current_user
from app.models.users import User
from app.services.email import EmailService


router = APIRouter()


email_service = EmailService()


@router.post("/test-email")
async def test_email(
    current_user: User = Depends(get_current_user),
):
    result = await email_service.send_email(
        to=current_user.email,
        subject="Fitness App — тестовое письмо",
        html="""
        <h1>Привет!</h1>

        <p>
            Если ты видишь это письмо,
            Resend работает.
        </p>

        <p>
            Твоя почтовая система подключена
            к Fitness App.
        </p>
        """,
    )

    return {
        "message": "Email sent",
        "email": current_user.email,
        # "result": result,  # можно раскомментировать для отладки
    }