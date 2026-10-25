from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.progress_photo import ProgressPhoto


class ProgressPhotoRepository:
    def __init__(self):
        pass

    async def get_by_id(self, db: AsyncSession, photo_id: int) -> ProgressPhoto | None:
        stmt = select(ProgressPhoto).where(ProgressPhoto.id == photo_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ProgressPhoto]:
        stmt = (
            select(ProgressPhoto)
            .where(ProgressPhoto.user_id == user_id)
            .order_by(ProgressPhoto.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(self, db: AsyncSession, photo_db: ProgressPhoto) -> ProgressPhoto:
        db.add(photo_db)
        return photo_db

    def update(self, db: AsyncSession, photo_db: ProgressPhoto) -> ProgressPhoto:
        return photo_db

    async def delete(self, db: AsyncSession, photo_db: ProgressPhoto) -> None:
        await db.delete(photo_db)