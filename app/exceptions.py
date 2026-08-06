class AppError(Exception):
    """
    Базовый класс чтобы не перечислять ошибки все, а писать except AppError as e:
    log.warning(f"Бизнес-ошибка: {e}")
    """
    pass


class UserNotFoundError(AppError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Бро человека в базе данных с id={user_id} нет!")


class EmailAlreadyExistsError(AppError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email {email} уже занят, бро")

class LoginAlreadyExistsError(AppError):
    def __init__(self, login: str):
        self.login = login
        super().__init__(f"Логин {login} уже занят дружище")


class InvalidPasswordError(AppError):
    def __init__(self):
        super().__init__("Неверный пароль, надо подумать")

class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__("Неверный логин или пароль")

class ForbiddenError(AppError):
    def __init__(self):
        super().__init__("У вас недостаточно прав для выполнения этого действия")
class EmailNotVerifiedError(AppError):
    def __init__(self):
        super().__init__("У вас не подтвержден email")



class ExerciseNotFoundError(AppError):
    def __init__(self, exercise_id: int):
        self.exercise_id = exercise_id
        super().__init__(f"Упражнения с id={exercise_id} в базе нет, бро!")

class ExerciseAlreadyExistsError(AppError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Упражнение '{name}' уже существует в справочнике, дружище")

class MuscleGroupNotFoundError(AppError):
    def __init__(self, muscle_group_id: int):
        self.muscle_group_id = muscle_group_id
        super().__init__(f"Группы мышц с id={muscle_group_id} не найдено!")

class EquipmentNotFoundError(AppError):
    def __init__(self, equipment_id: int):
        self.equipment_id = equipment_id
        super().__init__(f"Оборудования с id={equipment_id} не найдено!")


class ProgramNotFoundError(AppError):
    def __init__(self, program_id: int):
        self.program_id = program_id
        super().__init__(f"Программы с id={program_id} не найдено!")