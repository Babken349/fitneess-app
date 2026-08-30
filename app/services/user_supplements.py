from sqlalchemy.orm import Session

from app.models.user_supplements import UserSupplement
from app.models.users import User

from app.schemas.user_supplements import (
    UserSupplementCreate,
    UserSupplementUpdate,
)

from app.repository.user_supplements import UserSupplementRepository
from app.repository.supplement_repository import SupplementRepository

from app.exceptions import (
    UserSupplementNotFoundError,
    UserSupplementAlreadyExistsError,
    SupplementNotFoundError,
    ForbiddenError,
)


class UserSupplementService:

    def __init__(self):
        self.user_supplement_repo = UserSupplementRepository()
        self.supplement_repo = SupplementRepository()

    # =========================
    # CREATE
    # =========================

    def create_user_supplement(
        self,
        db: Session,
        data: UserSupplementCreate,
        current_user: User,
    ) -> UserSupplement:

        supplement = self.supplement_repo.get_by_id(
            db,
            data.supplement_id,
        )

        if not supplement:
            raise SupplementNotFoundError(
                data.supplement_id
            )

        existing = (
            self.user_supplement_repo.get_by_user_and_supplement(
                db,
                current_user.id,
                data.supplement_id,
            )
        )

        if existing:
            raise UserSupplementAlreadyExistsError(
                data.supplement_id
            )

        user_supplement = UserSupplement(
            user_id=current_user.id,
            supplement_id=data.supplement_id,
            dosage=data.dosage,
        )

        self.user_supplement_repo.create(
            db,
            user_supplement,
        )

        db.commit()
        db.refresh(user_supplement)

        return user_supplement

    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        db: Session,
        user_supplement_id: int,
        current_user: User,
    ) -> UserSupplement:

        user_supplement = (
            self.user_supplement_repo.get_by_id(
                db,
                user_supplement_id,
            )
        )

        if not user_supplement:
            raise UserSupplementNotFoundError(
                user_supplement_id
            )

        if user_supplement.user_id != current_user.id:
            raise ForbiddenError()

        return user_supplement

    # =========================
    # GET MY SUPPLEMENTS
    # =========================

    def get_my_supplements(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserSupplement]:

        return self.user_supplement_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    # =========================
    # UPDATE
    # =========================

    def update_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        data: UserSupplementUpdate,
        current_user: User,
    ) -> UserSupplement:

        user_supplement = self.get_by_id(
            db,
            user_supplement_id,
            current_user,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                user_supplement,
                key,
                value,
            )

        self.user_supplement_repo.update(
            user_supplement
        )

        db.commit()
        db.refresh(user_supplement)

        return user_supplement

    # =========================
    # DELETE
    # =========================

    def delete_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        current_user: User,
    ) -> None:

        user_supplement = self.get_by_id(
            db,
            user_supplement_id,
            current_user,
        )

        self.user_supplement_repo.delete(
            db,
            user_supplement,
        )

        db.commit()