from fastapi import FastAPI, Request
from app.api.v1.users import router as users_router
from app.api.v1.auth import router as auth_router
from fastapi.responses import JSONResponse 
from app.exceptions import (
    AppError,
    UserNotFoundError,
    EmailAlreadyExistsError,
    LoginAlreadyExistsError,
    InvalidPasswordError,
    ForbiddenError,
    EmailNotVerifiedError,
)

app = FastAPI()


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(LoginAlreadyExistsError)
async def login_exists_handler(request: Request, exc: LoginAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidPasswordError)
async def invalid_password_handler(request: Request, exc: InvalidPasswordError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    # запасной обработчик — ловит любую доменную ошибку,
    # для которой не зарегистрирован персональный handler выше
    return JSONResponse(status_code=400, content={"detail": str(exc)})



@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

@app.exception_handler(EmailNotVerifiedError)
async def forbidden_error_handler(request: Request, exc: EmailNotVerifiedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])