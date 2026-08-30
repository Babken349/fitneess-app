from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.achievement import Achievement


class AchievementRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, achievement_id: int) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.id == achievement_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_code(self, db: Session, code: str) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.code == code)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.name == name)
        return db.execute(stmt).scalar_one_or_none()

    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> list[Achievement]:
        stmt = select(Achievement).offset(skip).limit(limit)
        return db.execute(stmt).scalars().all()

    def get_all_active(self, db: Session, skip: int = 0, limit: int = 20) -> list[Achievement]:
        stmt = (
            select(Achievement)
            .where(Achievement.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def create(self, db: Session, achievement_db: Achievement) -> Achievement:
        db.add(achievement_db)
        return achievement_db

    def update(self, achievement_db: Achievement) -> Achievement:
        return achievement_db

    def exists_by_code(self, db: Session, code: str) -> bool:
        stmt = select(Achievement).where(Achievement.code == code)
        return db.execute(stmt).scalar_one_or_none() is not None

    def exists_by_name(self, db: Session, name: str) -> bool:
        stmt = select(Achievement).where(Achievement.name == name)
        return db.execute(stmt).scalar_one_or_none() is not None