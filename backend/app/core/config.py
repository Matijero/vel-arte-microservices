from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Información de la aplicación
    app_name: str = "Sistema de Gestión de Velas Vel Arte"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Base de datos SIN autenticación para empezar
    database_url: str = "mongodb://localhost:27017/"
    database_name: str = "velas_db"
    
    # Seguridad
    secret_key: str = "tu-super-secreto-muy-largo-y-complejo-cambiar-en-produccion-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS - Orígenes permitidos
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()
