from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_state import StudyState
from app.models.users import User

from app.repository.study_state import StudyStateRepository
from app.schemas.study_state import StudyStateCreate
from app.exceptions import StudyStateNotFoundError, ForbiddenError

class StudyStateService:

    def __init__(self):
        self.study_state_repo = StudyStateRepository()

    async def create(
        self,
        db: AsyncSession,
        data: StudyStateCreate,
        current_user: User,
    ) -> StudyState:

        study_state = StudyState(
            user_id=current_user.id,
            concentration=data.concentration,
            energy=data.energy,
            fatigue=data.fatigue,
            motivation=data.motivation,
            subject=data.subject,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
        )

        await self.study_state_repo.create(
            db,
            study_state,
        )

        await db.commit()
        await db.refresh(study_state)

        return study_state

    async def get_by_id(
        self,
        db: AsyncSession,
        study_state_id: int,
        current_user: User,
    ) -> StudyState:

        study_state = await self.study_state_repo.get_by_id(
            db,
            study_state_id,
        )

        if not study_state:
            raise StudyStateNotFoundError(study_state_id)

        if study_state.user_id != current_user.id:
            raise ForbiddenError()

        return study_state

    async def get_my_states(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[StudyState]:

        return await self.study_state_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    async def delete(
        self,
        db: AsyncSession,
        study_state_id: int,
        current_user: User,
    ) -> None:

        study_state = await self.get_by_id(
            db,
            study_state_id,
            current_user,
        )

        await self.study_state_repo.delete(
            db,
            study_state,
        )

        await db.commit()