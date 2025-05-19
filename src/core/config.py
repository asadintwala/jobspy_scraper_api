'''importing required modules.'''
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    '''Settings class to save settings'''
    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 10
    CACHE_EXPIRE_SECONDS: int = 300
    MONGODB_URL : str
    DB_NAME : str
    COLLECTION_NAME : str

    class Config:
        '''Config class to save .env'''
        env_file = ".env"
        case_sensitive = False

settings = Settings()
