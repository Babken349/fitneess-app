from sqlalchemy.orm import Session

from app.models.body_weight import BodyWeight
from app.models.users import User
from app.schemas.body_weight import BodyWeightCreate, BodyWeightUpdate
from app.repository.body_weight import BodyWeightRepository

from app.exceptions import BodyWeightNotFoundError, ForbiddenError


class BodyWeightService:
    def __init__(self):
        self.weight_repo = BodyWeightRepository()

    def create_weight(
        self,
        db: Session,
        data: BodyWeightCreate,
        current_user: User,
    ) -> BodyWeight:
        weight_db = BodyWeight(
            user_id=current_user.id,
            weight=data.weight,
        )

        new_weight = self.weight_repo.create(db, weight_db)
        db.commit()
        db.refresh(new_weight)
        return new_weight

    def get_by_id(
        self,
        db: Session,
        weight_id: int,
        current_user: User,
    ) -> BodyWeight:
        weight = self.weight_repo.get_by_id(db, weight_id)
        if not weight:
            raise BodyWeightNotFoundError(weight_id)

        if weight.user_id != current_user.id:
            raise ForbiddenError()

        return weight

    def get_my_weights(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyWeight]:
        return self.weight_repo.get_by_user(db, current_user.id, skip, limit)

    def update_weight(
        self,
        db: Session,
        weight_id: int,
        data: BodyWeightUpdate,
        current_user: User,
    ) -> BodyWeight:
        weight_db = self.get_by_id(db, weight_id, current_user)

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(weight_db, key, value)


        self.weight_repo.update(db, weight_db)
        db.commit()
        db.refresh(weight_db)
        return weight_db


    def delete_weight(
        self,
        db: Session,
        weight_id: int,
        current_user: User,
    ) -> None:
        weight_db = self.get_by_id(db, weight_id, current_user)
        self.weight_repo.delete(db, weight_db)
        db.commit()