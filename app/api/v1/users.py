from app.auth.dependencies import get_current_user, require_admin, require_premium
from app.models.users import User
from app.schemas.users import UserCreate, UserResponse
from app.core.dependency import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.services import users as users_service, auth
from app.repository import refresh_tokens as refresh_repository
from app.schemas.auth import Token, RefreshTokenRequest


router = APIRouter()


@router.get("/me", response_model=UserResponse, status_code=200)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
 
@router.post("/register", response_model=UserResponse, status_code=201)
def user_register(user_db: UserCreate, db: Session = Depends(get_db)):
    user = users_service.create_user(db=db, user=user_db)

    return user


@router.get("/admin-panel", response_model=UserResponse, status_code=200)
def get_admin_panel(current_user: User = Depends(require_admin)):
    return current_user

@router.get("/premium-content", response_model=UserResponse, status_code=200)
def get_premium_status(current_user: User = Depends(require_premium)):
    return current_user

@router.post("/refresh", response_model=Token,)
def refresh_access_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    token = auth.refresh_token(db, token_data)

    return token


@router.post("/logout")
def logout_refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    auth.logout(db, token_data)
    return {"message": "Successfully logged out"}


@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def get_user(user_id: int, db:Session = Depends(get_db)):
    user = users_service.get_user_by_id(db=db, user_id=user_id)
    return user
