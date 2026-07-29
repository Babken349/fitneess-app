from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    def hash(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)


password_manager = PasswordManager()