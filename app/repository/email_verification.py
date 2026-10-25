from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_token import EmailVerificationToken


class RepositoryEmailVerification:

    def create(
        self,
        db: AsyncSession,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        db.add(token)

        return token

    async def get_by_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> EmailVerificationToken | None:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.token == token
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[EmailVerificationToken]:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id
        )

        result = await db.execute(stmt)

        return result.scalars().all()

    async def get_active_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[EmailVerificationToken]:

        stmt = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used == False,
        )

        result = await db.execute(stmt)

        return result.scalars().all()

    def update(
        self,
        token: EmailVerificationToken,
    ) -> EmailVerificationToken:

        return token

    async def delete(
        self,
        db: AsyncSession,
        token: EmailVerificationToken,
    ) -> None:

        await db.delete(token)

    async def delete_active_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> None:

        stmt = delete(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used == False,
        )

        await db.execute(stmt)