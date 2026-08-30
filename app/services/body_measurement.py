from sqlalchemy.orm import Session

from app.models.body_measurement import BodyMeasurement
from app.models.users import User
from app.schemas.body_measurement import (
    BodyMeasurementCreate,
    BodyMeasurementUpdate,
)
from app.repository.body_measurement import BodyMeasurementRepository

from app.exceptions import (
    BodyMeasurementNotFoundError,
    EmptyBodyMeasurementError,
    ForbiddenError,
)


MEASUREMENT_FIELDS = ("chest", "waist", "hips", "biceps", "thigh", "forearm", "calf")


class BodyMeasurementService:
    def __init__(self):
        self.measurement_repo = BodyMeasurementRepository()

    def create_measurement(
        self,
        db: Session,
        data: BodyMeasurementCreate,
        current_user: User,
    ) -> BodyMeasurement:
        values = data.model_dump()
        if all(values[field] is None for field in MEASUREMENT_FIELDS):
            raise EmptyBodyMeasurementError()

        measurement_db = BodyMeasurement(
            user_id=current_user.id,
            **values,
        )

        new_measurement = self.measurement_repo.create(db, measurement_db)
        db.commit()
        db.refresh(new_measurement)
        return new_measurement

    def get_by_id(
        self,
        db: Session,
        measurement_id: int,
        current_user: User,
    ) -> BodyMeasurement:
        measurement = self.measurement_repo.get_by_id(db, measurement_id)
        if not measurement:
            raise BodyMeasurementNotFoundError(measurement_id)

        if measurement.user_id != current_user.id:
            raise ForbiddenError()

        return measurement

    def get_my_measurements(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyMeasurement]:
        return self.measurement_repo.get_by_user(db, current_user.id, skip, limit)

    def update_measurement(
        self,
        db: Session,
        measurement_id: int,
        data: BodyMeasurementUpdate,
        current_user: User,
    ) -> BodyMeasurement:
        measurement_db = self.get_by_id(db, measurement_id, current_user)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(measurement_db, key, value)

        self.measurement_repo.update(db, measurement_db)
        db.commit()
        db.refresh(measurement_db)
        return measurement_db



    def delete_measurement(
        self,
        db: Session,
        measurement_id: int,
        current_user: User,
    ) -> None:
        measurement_db = self.get_by_id(db, measurement_id, current_user)
        self.measurement_repo.delete(db, measurement_db)
        db.commit()