from passlib.context import CryptContext
from starlette.concurrency import run_in_threadpool

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    async def hash(self, plain: str) -> str:
        return await run_in_threadpool(pwd_context.hash, plain)

    async def verify(self, plain: str, hashed: str) -> bool:
        return await run_in_threadpool(pwd_context.verify, plain, hashed)


password_manager = PasswordManager()