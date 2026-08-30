from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "6eba8e246c86232cd57bd348768f671c3cd3966754f0f593ad0d952d25a6fdc9"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    RESEND_API_KEY: str
    EMAIL_FROM: str
    FRONTEND_URL: str 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()