'''importing required modules.'''
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    '''Settings class to save settings'''
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    CACHE_EXPIRE_SECONDS: int = 300

    class Config:
        '''Config class to save .env'''
        env_file = ".env"

settings = Settings()
