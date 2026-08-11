class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# ===========================
# Users
# ===========================

class UserNotFoundError(AppError):
    status_code = 404

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(
            f"Бро человека в базе данных с id={user_id} нет!"
        )


class EmailAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, email: str):
        self.email = email
        super().__init__(
            f"Email {email} уже занят, бро"
        )


class LoginAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, login: str):
        self.login = login
        super().__init__(
            f"Логин {login} уже занят, дружище"
        )


class InvalidPasswordError(AppError):
    status_code = 401

    def __init__(self):
        super().__init__(
            "Неверный пароль, надо подумать"
        )


class InvalidCredentialsError(AppError):
    status_code = 401

    def __init__(self):
        super().__init__(
            "Неверный логин или пароль"
        )


class ForbiddenError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "У вас недостаточно прав для выполнения этого действия"
        )


class EmailNotVerifiedError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "У вас не подтвержден email"
        )


# ===========================
# Exercises
# ===========================

class ExerciseNotFoundError(AppError):
    status_code = 404

    def __init__(self, exercise_id: int):
        self.exercise_id = exercise_id
        super().__init__(
            f"Упражнение с id={exercise_id} в базе не найдено!"
        )


class ExerciseAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Упражнение '{name}' уже существует в справочнике"
        )


class MuscleGroupNotFoundError(AppError):
    status_code = 404

    def __init__(self, muscle_group_id: int):
        self.muscle_group_id = muscle_group_id
        super().__init__(
            f"Группа мышц с id={muscle_group_id} не найдена!"
        )


class EquipmentNotFoundError(AppError):
    status_code = 404

    def __init__(self, equipment_id: int):
        self.equipment_id = equipment_id
        super().__init__(
            f"Оборудование с id={equipment_id} не найдено!"
        )


# ===========================
# Workout Programs
# ===========================

class ProgramNotFoundError(AppError):
    status_code = 404

    def __init__(self, program_id: int):
        self.program_id = program_id
        super().__init__(
            f"Программа с id={program_id} не найдена!"
        )


class InvalidProgramNameError(AppError):
    status_code = 400

    def __init__(self, program_name: str = ""):
        self.program_name = program_name
        super().__init__(
            "Некорректное название программы"
        )


class ProgramAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Программа '{name}' уже существует"
        )


class ProgramAccessDeniedError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "Вы не можете изменять чужую программу"
        )


class ProgramArchivedError(AppError):
    status_code = 400

    def __init__(self):
        super().__init__(
            "Программа уже архивирована"
        )


class EmptyProgramError(AppError):
    status_code = 400

    def __init__(self):
        super().__init__(
            "Программа не содержит ни одного тренировочного дня"
        )


# ===========================
# Workout Days
# ===========================

class DayNotFoundError(AppError):
    status_code = 404

    def __init__(self, day_id: int):
        self.day_id = day_id
        super().__init__(
            f"Тренировочный день с id={day_id} не найден!"
        )


class DayAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Тренировочный день '{name}' уже существует в этой программе"
        )


class InvalidDayNameError(AppError):
    status_code = 400

    def __init__(self, name: str = ""):
        self.name = name
        super().__init__(
            "Некорректное название тренировочного дня"
        )


class DayOrderAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, day_order: int):
        self.day_order = day_order
        super().__init__(
            f"Порядок тренировочного дня {day_order} уже занят!"
        )


class DayAccessDeniedError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "Вы не можете изменять тренировочный день чужой программы"
        )


class DayArchivedError(AppError):
    status_code = 400

    def __init__(self):
        super().__init__(
            "Тренировочный день уже архивирован"
        )


class DayNotArchivedError(AppError):
    status_code = 400

    def __init__(self):
        super().__init__(
            "Тренировочный день не находится в архиве"
        )

class WorkoutExerciseNotFoundError(AppError):
    status_code = 404

    def __init__(self, workout_exercise_id: int):
        self.workout_exercise_id = workout_exercise_id
        super().__init__(
            f"Упражнение в тренировке с id={workout_exercise_id} не найдено"
        )


class WorkoutDayNotFoundError(AppError):
    status_code = 404

    def __init__(self, workout_day_id: int):
        self.workout_day_id = workout_day_id
        super().__init__(
            f"Тренировочный день с id={workout_day_id} не найден"
        )


class WorkoutDayAccessDeniedError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "Вы не можете изменять упражнения в чужом тренировочном дне"
        )


class WorkoutExerciseAlreadyExistsError(AppError):
    status_code = 409

    def __init__(
        self,
        exercise_id: int,
        workout_day_id: int,
    ):
        self.exercise_id = exercise_id
        self.workout_day_id = workout_day_id

        super().__init__(
            "Это упражнение уже добавлено в данный тренировочный день"
        )


class WorkoutExerciseOrderAlreadyExistsError(AppError):
    status_code = 409

    def __init__(
        self,
        exercise_order: int,
        workout_day_id: int,
    ):
        self.exercise_order = exercise_order
        self.workout_day_id = workout_day_id

        super().__init__(
            f"Позиция упражнения {exercise_order} "
            f"в тренировочном дне уже занята"
        )

class WorkoutSessionNotFoundError(AppError):
    status_code = 404

    def __init__(self, session_id: int):
        self.session_id = session_id
        super().__init__(
            f"Тренировка с id={session_id} не найдена"
        )


class WorkoutSessionAccessDeniedError(AppError):
    status_code = 403

    def __init__(self):
        super().__init__(
            "Вы не можете изменять чужую тренировку"
        )


class WorkoutSessionAlreadyFinishedError(AppError):
    status_code = 400

    def __init__(self):
        super().__init__(
            "Тренировка уже завершена"
        )


class ActiveWorkoutSessionAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self):
        super().__init__(
            "У пользователя уже есть активная тренировка"
        )



class WorkoutSessionNotFoundError(AppError):
    status_code = 404

    def __init__(self, session_id: int):
        self.session_id = session_id
        super().__init__(
            f"Тренировка с id={session_id} не найдена"
        )


class ExerciseLogNotFoundError(AppError):
    status_code = 404

    def __init__(self, exercise_log_id: int):
        self.exercise_log_id = exercise_log_id
        super().__init__(
            f"ExerciseLog с id={exercise_log_id} не найден"
        )


class ExerciseLogAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, exercise_id: int):
        self.exercise_id = exercise_id
        super().__init__(
            f"Это упражнение уже добавлено в данную тренировку"
        )


class ExerciseOrderAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, exercise_order: int):
        self.exercise_order = exercise_order
        super().__init__(
            f"Порядок упражнения {exercise_order} уже занят"
        )


class SetLogNotFoundError(AppError):
    status_code = 404

    def __init__(self, set_log_id: int):
        self.set_log_id = set_log_id
        super().__init__(
            f"Подход с id={set_log_id} не найден"
        )


class SetAlreadyExistsError(AppError):
    status_code = 409

    def __init__(self, set_number: int):
        self.set_number = set_number
        super().__init__(
            f"Подход №{set_number} уже существует"
        )