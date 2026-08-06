
from app.models.users import User
from app.models.workout_program import WorkoutProgram
from app.repository.workout_program import WorkoutProgramRepository
from app.schemas.workout_program import CreateWorkoutProgram
from app.exceptions import ForbiddenError, ProgramAlreadyExistsError, ProgramNotFoundError
class ProgramService:
    def __init__(self):
        self.workout_program_repo = WorkoutProgramRepository()


    def create_program(self, db, program_data: CreateWorkoutProgram, current_user: User) -> WorkoutProgram:

        if program_data.name.strip() == "":
            raise ValueError(program_data.name)
        get_by_name_and_user = self.workout_program_repo.get_by_name_and_user(db, program_data.name, current_user.id)

        if get_by_name_and_user:
            raise ProgramAlreadyExistsError("Программа с таким названием уже существует")
        
        program_db = WorkoutProgram(
            user_id = current_user.id,
            name = program_data.name,
            description = program_data.description,
            is_public = program_data.is_public,
        )

        new_program = self.workout_program_repo.create(db, program_db)

        db.commit()
        db.refresh(new_program)
        return new_program


    def update_program(self, db, program_id: int, program_data: CreateWorkoutProgram, current_user: User) -> WorkoutProgram:
        program_db = self.workout_program_repo.get_by_id(db, program_id)

        if not program_db:
            raise ProgramNotFoundError(program_id)

        if program_db.user_id != current_user.id:
            raise ForbiddenError("Вы не можете редактировать чужую программу")

        if not program_data.name.strip():
            raise ValueError(program_data.name)

        get_by_name_and_user = self.workout_program_repo.get_by_name_and_user(db, program_data.name, current_user.id)

        if get_by_name_and_user and get_by_name_and_user.id != program_id:
            raise ProgramAlreadyExistsError("Программа с таким названием уже существует")

        program_db.name = program_data.name
        program_db.description = program_data.description
        program_db.is_public = program_data.is_public

        db.commit()
        db.refresh(program_db)
        return program_db


    def get_program_by_id(self, db: Session, program_id: int) -> WorkoutProgram | None:
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        return program

    def get_my_programs(self, db, current_user, skip, limit):
        return self.workout_program_repo.get_by_user(db, current_user.id, skip=skip, limit=limit)

    def get_public_programs(self, db: Session, skip: int = 0, limit: int = 20):
        return self.workout_program_repo.get_public(db, skip, limit)

    def search_programs(self, db: Session, name: str):
        return self.workout_program_repo.search_by_name(db, name)

    def archive_program(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        program.is_archived = True

        db.commit()
        db.refresh(program)

        return program
    
    def unarchive_program(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        program.is_archived = False

        db.commit()
        db.refresh(program)

        return program

    def delete_program(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        self.workout_program_repo.delete(db, program)

        db.commit()

    def make_public(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        program.is_public = True

        db.commit()
        db.refresh(program)

        return program

    def make_private(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        program.is_public = False

        db.commit()
        db.refresh(program)

        return program


    def get_my_program(self, db: Session, program_id: int, current_user: User):
        program = self.workout_program_repo.get_by_id(db, program_id)

        if not program:
            raise ProgramNotFoundError()

        if program.user_id != current_user.id:
            raise ForbiddenError()

        return program

    def get_archived_by_user(self, db: Session, user_id: int) -> list[WorkoutProgram]:
        return self.workout_program_repo.get_archived_by_user(db, user_id)

    def get_active_by_user(self, db: Session, user_id: int) -> list[WorkoutProgram]:
        return self.workout_program_repo.get_active_by_user(db, user_id)