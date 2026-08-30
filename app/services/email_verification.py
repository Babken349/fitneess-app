from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken
from app.models.users import User

from app.repository.email_verification import (
    RepositoryEmailVerification,
)

from app.repository import users as users_repository

from app.services.email import EmailService

from app.exceptions import (
    EmailVerificationTokenNotFoundError,
    EmailVerificationTokenExpiredError,
    EmailVerificationTokenAlreadyUsedError,
    EmailAlreadyVerifiedError,
)


class EmailVerificationService:

    def __init__(self):
        self.token_repo = RepositoryEmailVerification()
        self.email_service = EmailService()

    def create_verification_token(
        self,
        db: Session,
        user: User,
    ) -> EmailVerificationToken:

        self.token_repo.delete_active_by_user(
            db,
            user.id,
        )

        token = secrets.token_urlsafe(32)

        verification_token = EmailVerificationToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=30),
            used=False,
        )

        self.token_repo.create(
            db,
            verification_token,
        )

        db.commit()
        db.refresh(verification_token)

        return verification_token

    async def send_verification_email(
        self,
        db: Session,
        user: User,
    ):

        if user.is_verified:
            raise EmailAlreadyVerifiedError()

        verification_token = self.create_verification_token(
            db,
            user,
        )

        verification_url = (
            "http://localhost:8000/api/v1/"
            "email-verification/verify"
            f"?token={verification_token.token}"
        )

        await self.email_service.send_email(
            to=user.email,
            subject="Подтверждение email — Fitness App",
            html=f"""
            <h1>Подтверждение email</h1>

            <p>Привет, {user.display_name}!</p>

            <p>
                Нажми на кнопку ниже, чтобы подтвердить
                свой email.
            </p>

            <p>
                <a href="{verification_url}">
                    Подтвердить email
                </a>
            </p>

            <p>
                Ссылка действительна 30 минут.
            </p>
            """,
        )

    def verify_email(
        self,
        db: Session,
        token: str,
    ) -> User:

        verification_token = (
            self.token_repo.get_by_token(
                db,
                token,
            )
        )

        if not verification_token:
            raise EmailVerificationTokenNotFoundError()

        if verification_token.used:
            raise EmailVerificationTokenAlreadyUsedError()

        if verification_token.expires_at < datetime.now(
            timezone.utc
        ):
            raise EmailVerificationTokenExpiredError()

        user = users_repository.get_user_by_id(
            db,
            verification_token.user_id,
        )

        if not user:
            raise EmailVerificationTokenNotFoundError()

        if user.is_verified:
            raise EmailAlreadyVerifiedError()

        user.is_verified = True
        verification_token.used = True

        self.token_repo.update(
            verification_token
        )

        db.commit()
        db.refresh(user)

        return user