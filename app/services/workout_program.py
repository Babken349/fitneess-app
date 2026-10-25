from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.workout_program import WorkoutProgram
from app.repository.workout_program import WorkoutProgramRepository
from app.schemas.workout_program import CreateWorkoutProgram, WorkoutProgramUpdate
from app.exceptions import (
    ProgramAlreadyExistsError,
    ProgramNotFoundError,
    InvalidProgramNameError,
    ProgramAccessDeniedError,
    ProgramArchivedError,
)


class ProgramService:
    def __init__(self):
        self.workout_program_repo = WorkoutProgramRepository()


    async def create_program(
        self,
        db: AsyncSession,
        program_data: CreateWorkoutProgram,
        current_user: User,
    ) -> WorkoutProgram:

        if not program_data.name.strip():
            raise InvalidProgramNameError(program_data.name)

        existing = await self.workout_program_repo.get_by_name_and_user(
            db,
            program_data.name,
            current_user.id,
        )

        if existing:
            raise ProgramAlreadyExistsError(program_data.name)

        program_db = WorkoutProgram(
            user_id=current_user.id,
            name=program_data.name,
            description=program_data.description,
            is_public=program_data.is_public,
        )

        new_program = self.workout_program_repo.create(db, program_db)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ProgramAlreadyExistsError(program_data.name)

        await db.refresh(new_program)

        return new_program



    async def update_program(
        self,
        db: AsyncSession,
        program_id: int,
        program_data: WorkoutProgramUpdate,
        current_user: User,
    ) -> WorkoutProgram:

        program_db = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        update_data = program_data.model_dump(exclude_unset=True)

        # is_public в БД обязательное, явный null не применяем
        if "is_public" in update_data and update_data["is_public"] is None:
            del update_data["is_public"]

        if "name" in update_data:

            if update_data["name"] is None or not update_data["name"].strip():
                raise InvalidProgramNameError(update_data["name"])

            existing = await self.workout_program_repo.get_by_name_and_user(
                db,
                update_data["name"],
                current_user.id,
            )

            if existing and existing.id != program_id:
                raise ProgramAlreadyExistsError(update_data["name"])

        for key, value in update_data.items():
            setattr(program_db, key, value)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise ProgramAlreadyExistsError(update_data.get("name"))

        await db.refresh(program_db)

        return program_db



    async def get_program_by_id(
        self,
        db: AsyncSession,
        program_id: int,
    ) -> WorkoutProgram:

        program = await self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError(program_id)

        return program

    async def get_my_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_program_by_id(db, program_id)

        if program.user_id != current_user.id:
            raise ProgramAccessDeniedError()

        return program

    async def get_my_programs(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkoutProgram], int]:
        items = await self.workout_program_repo.get_by_user(
            db, current_user.id, skip=skip, limit=limit,
        )
        total = await self.workout_program_repo.count_by_user(
            db, current_user.id,
        )
        return items, total

    
    async def get_public_programs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkoutProgram], int]:
        items = await self.workout_program_repo.get_public(
            db, skip, limit,
        )
        total = await self.workout_program_repo.count_public(db)
        return items, total

    async def get_accessible_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_program_by_id(db, program_id)

        if program.user_id != current_user.id and not program.is_public:
            raise ProgramAccessDeniedError()

        return program

    async def search_programs(
        self,
        db: AsyncSession,
        name: str,
        current_user: User,
    ) -> list[WorkoutProgram]:

        return await self.workout_program_repo.search_by_name(
            db,
            name,
            current_user.id,
        )

    async def get_archived_by_user(
        self,
        db: AsyncSession,
        current_user: User,
    ) -> list[WorkoutProgram]:

        return await self.workout_program_repo.get_archived_by_user(
            db,
            current_user.id,
        )

    async def get_active_by_user(
        self,
        db: AsyncSession,
        current_user: User,
    ) -> list[WorkoutProgram]:

        return await self.workout_program_repo.get_active_by_user(
            db,
            current_user.id,
        )



    async def archive_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        if program.is_archived:
            raise ProgramArchivedError()

        program.is_archived = True

        await db.commit()
        await db.refresh(program)

        return program

    async def unarchive_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        program.is_archived = False

        await db.commit()
        await db.refresh(program)

        return program



    async def delete_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> None:

        program = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        await self.workout_program_repo.delete(
            db,
            program,
        )

        await db.commit()


    async def make_public(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        program.is_public = True

        await db.commit()
        await db.refresh(program)

        return program

    async def make_private(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> WorkoutProgram:

        program = await self.get_my_program(
            db,
            program_id,
            current_user,
        )

        program.is_public = False

        await db.commit()
        await db.refresh(program)

        return program