from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress_photo import ProgressPhoto
from app.models.users import User
from app.schemas.progress_photo import ProgressPhotoCreate, ProgressPhotoUpdate
from app.repository.progress_photo import ProgressPhotoRepository

from app.exceptions import ProgressPhotoNotFoundError, ForbiddenError


class ProgressPhotoService:
    def __init__(self):
        self.photo_repo = ProgressPhotoRepository()

    async def create_photo(
        self,
        db: AsyncSession,
        data: ProgressPhotoCreate,
        current_user: User,
    ) -> ProgressPhoto:
        photo_db = ProgressPhoto(
            user_id=current_user.id,
            image_url=data.image_url,
            notes=data.notes,
        )

        new_photo = self.photo_repo.create(db, photo_db)
        await db.commit()
        await db.refresh(new_photo)
        return new_photo

    async def get_by_id(
        self,
        db: AsyncSession,
        photo_id: int,
        current_user: User,
    ) -> ProgressPhoto:
        photo = await self.photo_repo.get_by_id(db, photo_id)
        if not photo:
            raise ProgressPhotoNotFoundError(photo_id)

        if photo.user_id != current_user.id:
            raise ForbiddenError()

        return photo

    async def get_my_photos(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ProgressPhoto]:
        return await self.photo_repo.get_by_user(db, current_user.id, skip, limit)

    async def update_photo(
        self,
        db: AsyncSession,
        photo_id: int,
        data: ProgressPhotoUpdate,
        current_user: User,
    ) -> ProgressPhoto:
        photo_db = await self.get_by_id(db, photo_id, current_user)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(photo_db, key, value)

        self.photo_repo.update(db, photo_db)
        await db.commit()
        await db.refresh(photo_db)
        return photo_db

    async def delete_photo(
        self,
        db: AsyncSession,
        photo_id: int,
        current_user: User,
    ) -> None:
        photo_db = await self.get_by_id(db, photo_id, current_user)
        await self.photo_repo.delete(db, photo_db)
        await db.commit()