from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.body_measurement import BodyMeasurement


class BodyMeasurementRepository:
    def __init__(self):
        pass

    def get_by_id(self, db: Session, measurement_id: int) -> BodyMeasurement | None:
        stmt = select(BodyMeasurement).where(BodyMeasurement.id == measurement_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyMeasurement]:
        stmt = (
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == user_id)
            .order_by(BodyMeasurement.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        return result.scalars().all()

    def create(self, db: Session, measurement_db: BodyMeasurement) -> BodyMeasurement:
        db.add(measurement_db)
        return measurement_db

    def update(self, db: Session, measurement_db: BodyMeasurement) -> BodyMeasurement:
        return measurement_db

    def delete(self, db: Session, measurement_db: BodyMeasurement) -> None:
        db.delete(measurement_db)