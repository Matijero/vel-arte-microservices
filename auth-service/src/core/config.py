from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configuración de base de datos (de tu .env)
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "vel_arte_auth"
    
    # Configuración JWT (de tu .env)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
