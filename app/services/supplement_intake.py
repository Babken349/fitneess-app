from datetime import datetime

from sqlalchemy.orm import Session

from app.models.supplement_intake import SupplementIntake
from app.models.users import User

from app.schemas.supplement_intake import (
    SupplementIntakeCreate,
    SupplementIntakeUpdate,
)

from app.repository.supplement_intake import (
    SupplementIntakeRepository,
)

from app.repository.user_supplements import (
    UserSupplementRepository,
)

from app.exceptions import (
    SupplementIntakeNotFoundError,
    SupplementIntakeAccessDeniedError,
    SupplementIntakeUserSupplementNotFoundError,
    SupplementIntakeInvalidStatusError,
)


class SupplementIntakeService:

    ALLOWED_STATUSES = {
        "taken",
        "skipped",
        "missed",
    }

    def __init__(self):
        self.intake_repo = SupplementIntakeRepository()
        self.user_supplement_repo = (
            UserSupplementRepository()
        )

    def _get_owned_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        current_user: User,
    ):

        user_supplement = (
            self.user_supplement_repo.get_by_id(
                db,
                user_supplement_id,
            )
        )

        if not user_supplement:
            raise SupplementIntakeUserSupplementNotFoundError(
                user_supplement_id
            )

        if user_supplement.user_id != current_user.id:
            raise SupplementIntakeAccessDeniedError(
                user_supplement_id
            )

        return user_supplement

    def create_intake(
        self,
        db: Session,
        data: SupplementIntakeCreate,
        current_user: User,
    ) -> SupplementIntake:

        self._get_owned_user_supplement(
            db,
            data.user_supplement_id,
            current_user,
        )

        if data.status not in self.ALLOWED_STATUSES:
            raise SupplementIntakeInvalidStatusError(
                data.status
            )

        intake = SupplementIntake(
            user_id=current_user.id,
            user_supplement_id=data.user_supplement_id,
            scheduled_at=data.scheduled_at,
            taken_at=data.taken_at,
            status=data.status,
            notes=data.notes,
        )

        self.intake_repo.create(
            db,
            intake,
        )

        db.commit()
        db.refresh(intake)

        return intake

    def get_by_id(
        self,
        db: Session,
        intake_id: int,
        current_user: User,
    ) -> SupplementIntake:

        intake = self.intake_repo.get_by_id(
            db,
            intake_id,
        )

        if not intake:
            raise SupplementIntakeNotFoundError(
                intake_id
            )

        if intake.user_id != current_user.id:
            raise SupplementIntakeAccessDeniedError(
                intake_id
            )

        return intake

    def get_my_intakes(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        return self.intake_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    def get_by_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        self._get_owned_user_supplement(
            db,
            user_supplement_id,
            current_user,
        )

        return self.intake_repo.get_by_user_supplement(
            db,
            user_supplement_id,
            skip,
            limit,
        )

    def get_by_status(
        self,
        db: Session,
        status: str,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:

        if status not in self.ALLOWED_STATUSES:
            raise SupplementIntakeInvalidStatusError(
                status
            )

        return self.intake_repo.get_by_status(
            db,
            current_user.id,
            status,
            skip,
            limit,
        )

    def update_intake(
        self,
        db: Session,
        intake_id: int,
        data: SupplementIntakeUpdate,
        current_user: User,
    ) -> SupplementIntake:

        intake = self.get_by_id(
            db,
            intake_id,
            current_user,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if "status" in update_data:
            if (
                update_data["status"]
                not in self.ALLOWED_STATUSES
            ):
                raise SupplementIntakeInvalidStatusError(
                    update_data["status"]
                )

        for key, value in update_data.items():
            setattr(
                intake,
                key,
                value,
            )

        self.intake_repo.update(
            intake,
        )

        db.commit()
        db.refresh(intake)

        return intake

    def delete_intake(
        self,
        db: Session,
        intake_id: int,
        current_user: User,
    ) -> None:

        intake = self.get_by_id(
            db,
            intake_id,
            current_user,
        )

        self.intake_repo.delete(
            db,
            intake,
        )

        db.commit()

    def get_my_intakes_by_date_range(
        self,
        db: Session,
        start_at: datetime,
        end_at: datetime,
        current_user: User,
    ) -> list[SupplementIntake]:

        return self.intake_repo.get_by_date_range(
            db,
            current_user.id,
            start_at,
            end_at,
        )