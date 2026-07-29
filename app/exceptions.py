class AppError(Exception):
    """
    Базовый класс чтобы не перечислять ошибки все, а писать except AppError as e:
    log.warning(f"Бизнес-ошибка: {e}")
    """
    pass


class UserNotFoundError(AppError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Бро чела с id={user_id} нет!")


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