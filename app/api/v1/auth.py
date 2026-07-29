from fastapi import APIRouter, Depends
from app.core.dependency import get_db
from app.schemas.auth import Token
from app.schemas.users import UserLogin
from app.services import auth
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    return auth.login(credentials=credentials, db=db)