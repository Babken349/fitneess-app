from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementUpdate
from app.repository.achievement import AchievementRepository

from app.exceptions import (
    AchievementNotFoundError,
    AchievementCodeNotFoundError,
    AchievementAlreadyExistsError,
    AchievementCodeAlreadyExistsError,
)


class AchievementService:
    def __init__(self):
        self.achievement_repo = AchievementRepository()

    def create_achievement(self, db: Session, data: AchievementCreate) -> Achievement:
        if self.achievement_repo.exists_by_code(db, data.code):
            raise AchievementCodeAlreadyExistsError(data.code)

        if self.achievement_repo.exists_by_name(db, data.name):
            raise AchievementAlreadyExistsError(data.name)

        achievement_db = Achievement(
            name=data.name,
            description=data.description,
            code=data.code,
            icon_url=data.icon_url,
        )

        new_achievement = self.achievement_repo.create(db, achievement_db)
        db.commit()
        db.refresh(new_achievement)
        return new_achievement

    def get_by_id(self, db: Session, achievement_id: int) -> Achievement:
        achievement = self.achievement_repo.get_by_id(db, achievement_id)
        if not achievement:
            raise AchievementNotFoundError(achievement_id)
        return achievement

    def get_by_code(self, db: Session, code: str) -> Achievement:
        achievement = self.achievement_repo.get_by_code(db, code)
        if not achievement:
            raise AchievementCodeNotFoundError(code)
        return achievement

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> list[Achievement]:
        return self.achievement_repo.get_all_active(db, skip, limit)

    def update_achievement(
        self, db: Session, achievement_id: int, data: AchievementUpdate
    ) -> Achievement:
        achievement_db = self.get_by_id(db, achievement_id)

        update_data = data.model_dump(exclude_unset=True)

        if "code" in update_data and update_data["code"] != achievement_db.code:
            if self.achievement_repo.exists_by_code(db, update_data["code"]):
                raise AchievementCodeAlreadyExistsError(update_data["code"])

        if "name" in update_data and update_data["name"] != achievement_db.name:
            if self.achievement_repo.exists_by_name(db, update_data["name"]):
                raise AchievementAlreadyExistsError(update_data["name"])

        for key, value in update_data.items():
            setattr(achievement_db, key, value)

        self.achievement_repo.update(achievement_db)
        db.commit()
        db.refresh(achievement_db)
        return achievement_db

    def deactivate_achievement(self, db: Session, achievement_id: int) -> Achievement:
        achievement_db = self.get_by_id(db, achievement_id)
        achievement_db.is_active = False

        self.achievement_repo.update(achievement_db)
        db.commit()
        db.refresh(achievement_db)
        return achievement_db