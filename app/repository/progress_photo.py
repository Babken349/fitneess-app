from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.progress_photo import ProgressPhoto


class ProgressPhotoRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, photo_id: int) -> ProgressPhoto | None:
        stmt = select(ProgressPhoto).where(ProgressPhoto.id == photo_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
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
        result = db.execute(stmt)
        return result.scalars().all()

    def create(self, db: Session, photo_db: ProgressPhoto) -> ProgressPhoto:
        db.add(photo_db)
        return photo_db

    def update(self, db: Session, photo_db: ProgressPhoto) -> ProgressPhoto:
        return photo_db

    def delete(self, db: Session, photo_db: ProgressPhoto) -> None:
        db.delete(photo_db)