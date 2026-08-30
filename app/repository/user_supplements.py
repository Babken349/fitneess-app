from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_supplements import UserSupplement


class UserSupplementRepository:

    def create(
        self,
        db: Session,
        user_supplement: UserSupplement,
    ) -> UserSupplement:

        db.add(user_supplement)

        return user_supplement

    def update(
        self,
        user_supplement: UserSupplement,
    ) -> UserSupplement:

        return user_supplement

    def delete(
        self,
        db: Session,
        user_supplement: UserSupplement,
    ) -> None:

        db.delete(user_supplement)

    def get_by_id(
        self,
        db: Session,
        user_supplement_id: int,
    ) -> UserSupplement | None:

        stmt = select(UserSupplement).where(
            UserSupplement.id == user_supplement_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_user_and_supplement(
        self,
        db: Session,
        user_id: int,
        supplement_id: int,
    ) -> UserSupplement | None:

        stmt = select(UserSupplement).where(
            UserSupplement.user_id == user_id,
            UserSupplement.supplement_id == supplement_id,
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserSupplement]:

        stmt = (
            select(UserSupplement)
            .where(UserSupplement.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()
