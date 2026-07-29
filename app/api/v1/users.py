from app.schemas.users import UserCreate, UserResponse
from app.core.dependency import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.services import users as users_service


router = APIRouter()


@router.post("/users/register", response_model=UserResponse, status_code=201)
def user_register(user_db: UserCreate, db:Session = Depends(get_db)):
    user = users_service.create_user(db=db, user=user_db)

    return user

@router.get("/users/{user_id}", response_model=UserResponse, status_code=201)
def get_user(user_id: int, db:Session = Depends(get_db)):
    user = users_service.get_user_by_id(db=db, user_id=user_id)
    return user