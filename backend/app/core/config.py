from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "IT Operations Analytics"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://it_ops:secure_password@mysql:3306/it_operations"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # EazyBI
    EAZYBI_BASE_URL: str = "https://aod.eazybi.com/accounts/59396/export/report"
    EAZYBI_API_KEY: Optional[str] = None
    EAZYBI_USERNAME: Optional[str] = None
    EAZYBI_PASSWORD: Optional[str] = None
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
