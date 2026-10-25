from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_test_result import StudyTestResult
from app.models.users import User

from app.repository.study_test_result import (
    StudyTestResultRepository,
)

from app.schemas.study_test_result import (
    StudyTestResultCreate,
)
from app.exceptions import (
    StudyTestResultNotFoundError,
    InvalidTestScoreError,
    ForbiddenError,
)

class StudyTestResultService:

    def __init__(self):
        self.result_repo = StudyTestResultRepository()

    async def create(
        self,
        db: AsyncSession,
        data: StudyTestResultCreate,
        current_user: User,
    ) -> StudyTestResult:

        if data.score > data.max_score:
            raise InvalidTestScoreError(data.score, data.max_score)

        result = StudyTestResult(
            user_id=current_user.id,
            exam_type=data.exam_type,
            subject=data.subject,
            score=data.score,
            max_score=data.max_score,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
        )

        await self.result_repo.create(
            db,
            result,
        )

        await db.commit()
        await db.refresh(result)

        return result

    async def get_by_id(
        self,
        db: AsyncSession,
        result_id: int,
        current_user: User,
    ) -> StudyTestResult:

        result = await self.result_repo.get_by_id(
            db,
            result_id,
        )

        if not result:
            raise StudyTestResultNotFoundError(result_id)

        if result.user_id != current_user.id:
            raise ForbiddenError()

        return result

    async def get_my_results(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[StudyTestResult]:

        return await self.result_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    async def delete(
        self,
        db: AsyncSession,
        result_id: int,
        current_user: User,
    ) -> None:

        result = await self.get_by_id(
            db,
            result_id,
            current_user,
        )

        await self.result_repo.delete(
            db,
            result,
        )

        await db.commit()