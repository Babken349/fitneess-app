from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user
from app.schemas.auth import Token, VerifyEmail, ForgotPassword, ResetPassword
from app.schemas.users import UserLogin
from app.models.users import User

# Импортируем нужные сервисы
from app.services import auth
from app.services import email_service
from app.services import password_reset_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    return auth.login(credentials=credentials, db=db)


@router.post("/request-verify")
def request_verify(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    email_service.request_verification_token(db=db, user=current_user)
    return {"message": "Письмо для подтверждения email отправлено"}


@router.post("/verify-email")
def verify_email(
    token_data: VerifyEmail, 
    db: Session = Depends(get_db)
):
    email_service.verify_email(db=db, token_string=token_data.token)
    return {"message": "Email успешно подтвержден"}


@router.post("/logout-all")
def logout_all_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth.logout_all(db, current_user)
    return {"message": "Вы вышли со всех устройств"}


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPassword,
    db: Session = Depends(get_db)
):
    # Вызываем сервис сброса пароля
    return password_reset_service.request_password_reset(db, data.email)


@router.post("/reset-password")
def reset_password(
    data: ResetPassword,
    db: Session = Depends(get_db)
):
    # Вызываем сервис сброса пароля
    return password_reset_service.reset_password(db, data.token, data.new_password)