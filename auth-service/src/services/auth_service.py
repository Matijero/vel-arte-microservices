from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import logging

logger = logging.getLogger(__name__)

# Configurar bcrypt para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Servicio de autenticación con JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        
        # Obtener configuración del environment
        secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
        algorithm = os.getenv("ALGORITHM", "HS256")
        
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt
    
    @staticmethod
    async def create_user(user_data: Dict) -> Dict:
        """Crear nuevo usuario (simulado por ahora)"""
        try:
            logger.info(f"Creando usuario: {user_data.get('username')}")
            
            # Hash de la contraseña
            if "password" in user_data:
                user_data["password"] = AuthService.get_password_hash(user_data["password"])
            
            # Agregar timestamps
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            user_data["id"] = f"user_{user_data.get('username', 'unknown')}"
            
            # Por ahora, simular que el usuario se creó
            # TODO: Implementar conexión real a MongoDB
            
            # No devolver contraseña
            result = user_data.copy()
            if "password" in result:
                del result["password"]
            
            logger.info(f"Usuario creado exitosamente: {result['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise ValueError(f"Error creando usuario: {e}")
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[Dict]:
        """Autenticar usuario (simulado por ahora)"""
        try:
            logger.info(f"Autenticando usuario: {username}")
            
            # Por ahora, crear un usuario de prueba
            # TODO: Implementar búsqueda real en MongoDB
            if username == "admin" and password == "admin123":
                user = {
                    "id": "user_admin",
                    "username": username,
                    "email": "admin@velarte.com",
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                logger.info(f"Usuario autenticado exitosamente: {username}")
                return user
            
            logger.warning(f"Credenciales inválidas para: {username}")
            return None
            
        except Exception as e:
            logger.error(f"Error autenticando usuario {username}: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verificar token JWT"""
        try:
            secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
            algorithm = os.getenv("ALGORITHM", "HS256")
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role", "user")
            
            if username is None:
                return None
                
            return {"username": username, "role": role, "valid": True}
            
        except JWTError as e:
            logger.warning(f"Token inválido: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
