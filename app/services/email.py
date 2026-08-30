import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


class EmailService:
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
    ) -> dict | None:
        """
        Отправка email через Resend.
        Возвращает ответ от API (если нужно) или None.
        """
        payload = {
            "from": f"Onboarding <{settings.EMAIL_FROM}>",
            "to": to,
            "subject": subject,
            "html": html,
        }

        if text:
            payload["text"] = text

        response = resend.Emails.send(payload)
        return response