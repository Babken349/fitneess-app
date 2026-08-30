from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.body_weight import BodyWeight


class BodyWeightRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, weight_id: int) -> BodyWeight | None:
        stmt = select(BodyWeight).where(BodyWeight.id == weight_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyWeight]:
        stmt = (
            select(BodyWeight)
            .where(BodyWeight.user_id == user_id)
            .order_by(BodyWeight.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        return result.scalars().all()

    def create(self, db: Session, weight_db: BodyWeight) -> BodyWeight:
        db.add(weight_db)
        return weight_db

    def update(self, db: Session, weight_db: BodyWeight) -> BodyWeight:
        return weight_db

    def delete(self, db: Session, weight_db: BodyWeight) -> None:
        db.delete(weight_db)