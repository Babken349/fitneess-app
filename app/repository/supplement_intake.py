from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplement_intake import SupplementIntake


class SupplementIntakeRepository:

    def create(
        self,
        db: Session,
        intake: SupplementIntake,
    ) -> SupplementIntake:

        db.add(intake)
        return intake

    def update(
        self,
        intake: SupplementIntake,
    ) -> SupplementIntake:

        return intake

    def delete(
        self,
        db: Session,
        intake: SupplementIntake,
    ) -> None:

        db.delete(intake)

    def get_by_id(
        self,
        db: Session,
        intake_id: int,
    ) -> SupplementIntake | None:

        stmt = select(SupplementIntake).where(
            SupplementIntake.id == intake_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_id == user_id
            )
            .order_by(
                SupplementIntake.taken_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_supplement_id
                == user_supplement_id
            )
            .order_by(
                SupplementIntake.taken_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_status(
        self,
        db: Session,
        user_id: int,
        status: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_id == user_id,
                SupplementIntake.status == status,
            )
            .order_by(
                SupplementIntake.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_date_range(
        self,
        db: Session,
        user_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> list[SupplementIntake]:

        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_id == user_id,
                SupplementIntake.created_at >= start_at,
                SupplementIntake.created_at <= end_at,
            )
            .order_by(
                SupplementIntake.created_at.desc()
            )
        )

        return db.execute(stmt).scalars().all()