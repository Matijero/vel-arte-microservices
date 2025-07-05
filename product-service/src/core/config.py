from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configuración de base de datos
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "vel_arte_products"
    
    # Configuración de servicios
    auth_service_url: str = "http://auth-service:8000"
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Ignorar variables extra del entorno
        extra = "ignore"

settings = Settings()
