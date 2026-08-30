from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplements import Supplement


class SupplementRepository:

    def create(
        self,
        db: Session,
        supplement: Supplement,
    ) -> Supplement:
        db.add(supplement)
        return supplement

    def update(
        self,
        supplement: Supplement,
    ) -> Supplement:
        return supplement

    def delete(
        self,
        db: Session,
        supplement: Supplement,
    ) -> None:
        db.delete(supplement)

    def get_by_id(
        self,
        db: Session,
        supplement_id: int,
    ) -> Supplement | None:

        stmt = select(Supplement).where(
            Supplement.id == supplement_id
        )

        result = db.execute(stmt)

        return result.scalar_one_or_none()

    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> Supplement | None:

        stmt = select(Supplement).where(
            Supplement.name == name
        )

        result = db.execute(stmt)

        return result.scalar_one_or_none()

    def exists_by_name(
        self,
        db: Session,
        name: str,
    ) -> bool:

        stmt = select(Supplement).where(
            Supplement.name == name
        )

        return db.execute(stmt).scalar_one_or_none() is not None

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Supplement]:

        stmt = (
            select(Supplement)
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()