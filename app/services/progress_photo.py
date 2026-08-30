from sqlalchemy.orm import Session

from app.models.progress_photo import ProgressPhoto
from app.models.users import User
from app.schemas.progress_photo import ProgressPhotoCreate, ProgressPhotoUpdate
from app.repository.progress_photo import ProgressPhotoRepository

from app.exceptions import ProgressPhotoNotFoundError, ForbiddenError


class ProgressPhotoService:
    def __init__(self):
        self.photo_repo = ProgressPhotoRepository()

    def create_photo(
        self,
        db: Session,
        data: ProgressPhotoCreate,
        current_user: User,
    ) -> ProgressPhoto:
        photo_db = ProgressPhoto(
            user_id=current_user.id,
            image_url=data.image_url,
            notes=data.notes,
        )

        new_photo = self.photo_repo.create(db, photo_db)
        db.commit()
        db.refresh(new_photo)
        return new_photo

    def get_by_id(
        self,
        db: Session,
        photo_id: int,
        current_user: User,
    ) -> ProgressPhoto:
        photo = self.photo_repo.get_by_id(db, photo_id)
        if not photo:
            raise ProgressPhotoNotFoundError(photo_id)

        if photo.user_id != current_user.id:
            raise ForbiddenError()

        return photo

    def get_my_photos(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ProgressPhoto]:
        return self.photo_repo.get_by_user(db, current_user.id, skip, limit)

    def update_photo(
        self,
        db: Session,
        photo_id: int,
        data: ProgressPhotoUpdate,
        current_user: User,
    ) -> ProgressPhoto:
        photo_db = self.get_by_id(db, photo_id, current_user)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(photo_db, key, value)

        self.photo_repo.update(db, photo_db)
        db.commit()
        db.refresh(photo_db)
        return photo_db

    def delete_photo(
        self,
        db: Session,
        photo_id: int,
        current_user: User,
    ) -> None:
        photo_db = self.get_by_id(db, photo_id, current_user)
        self.photo_repo.delete(db, photo_db)
        db.commit()