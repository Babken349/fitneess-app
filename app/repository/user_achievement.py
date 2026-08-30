from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user_achievement import UserAchievement


class UserAchievementRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, user_achievement_id: int) -> UserAchievement | None:
        stmt = select(UserAchievement).where(UserAchievement.id == user_achievement_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_user_and_achievement(
        self, db: Session, user_id: int, achievement_id: int
    ) -> UserAchievement | None:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_user(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        stmt = (
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.earned_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def get_by_achievement(
        self, db: Session, achievement_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        stmt = (
            select(UserAchievement)
            .where(UserAchievement.achievement_id == achievement_id)
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, user_achievement_db: UserAchievement) -> UserAchievement:
        db.add(user_achievement_db)
        return user_achievement_db

    def delete(self, db: Session, user_achievement_db: UserAchievement) -> None:
        db.delete(user_achievement_db)

    def exists(self, db: Session, user_id: int, achievement_id: int) -> bool:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id,
        )
        return db.execute(stmt).scalar_one_or_none() is not None