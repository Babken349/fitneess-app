from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken


class RepositoryEmailVerification:

    def create(
        self,
        db: Session,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        db.add(token)

        return token

    def get_by_token(
        self,
        db: Session,
        token: str,
    ) -> EmailVerificationToken | None:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.token == token
        )

        result = db.execute(stmt)

        return result.scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[EmailVerificationToken]:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id
        )

        result = db.execute(stmt)

        return result.scalars().all()

    def get_active_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[EmailVerificationToken]:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used == False,
        )

        result = db.execute(stmt)

        return result.scalars().all()

    def update(
        self,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        return token

    def delete(
        self,
        db: Session,
        token: EmailVerificationToken,
    ) -> None:

        db.delete(token)

    def delete_active_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> None:

        stmt = delete(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used == False,
        )

        db.execute(stmt)