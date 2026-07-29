from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_new_password

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length = 8, max_length = 128)
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_new_password(value)
    
class VerifyEmail(BaseModel):
    token: str