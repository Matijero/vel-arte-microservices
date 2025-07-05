#!/bin/bash
echo "🏗️ IMPLEMENTANDO CLEAN ARCHITECTURE EN AUTH-SERVICE"

# Crear estructura de carpetas
mkdir -p auth-service/src/{domain,application,infrastructure,presentation}
mkdir -p auth-service/src/domain/{entities,value_objects,repositories,services}
mkdir -p auth-service/src/application/{use_cases,dto,interfaces}
mkdir -p auth-service/src/infrastructure/{database,repositories,external_services}
mkdir -p auth-service/src/presentation/{api,schemas}

# 1. DOMAIN LAYER - Entidades
cat > auth-service/src/domain/entities/user.py << 'ENTITY'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects import Email, UserId, HashedPassword

@dataclass
class User:
    """Entidad de dominio User - Reglas de negocio"""
    id: UserId
    email: Email
    username: str
    hashed_password: HashedPassword
    full_name: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desactivar usuario"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activar usuario"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_password(self, new_password: HashedPassword) -> None:
        """Actualizar contraseña"""
        self.hashed_password = new_password
        self.updated_at = datetime.utcnow()
ENTITY

# 2. VALUE OBJECTS
cat > auth-service/src/domain/value_objects/__init__.py << 'VO'
from typing import NewType
import re
from dataclasses import dataclass

# Type definitions
UserId = NewType('UserId', str)
HashedPassword = NewType('HashedPassword', str)

@dataclass(frozen=True)
class Email:
    """Value Object para Email con validación"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value
VO

# 3. REPOSITORY INTERFACE
cat > auth-service/src/domain/repositories/user_repository.py << 'REPO'
from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user import User
from ..value_objects import UserId, Email

class UserRepository(ABC):
    """Interface del repositorio - Domain layer"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Crear nuevo usuario"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Buscar usuario por ID"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Buscar usuario por email"""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Buscar usuario por username"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualizar usuario"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Eliminar usuario"""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Listar todos los usuarios"""
        pass
REPO

# 4. USE CASES
cat > auth-service/src/application/use_cases/register_user.py << 'USECASE'
from dataclasses import dataclass
from typing import Optional
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects import Email, UserId, HashedPassword
from ..dto.user_dto import CreateUserDTO, UserResponseDTO
from ..interfaces.password_hasher import PasswordHasher
import uuid

@dataclass
class RegisterUserUseCase:
    """Caso de uso: Registrar nuevo usuario"""
    user_repository: UserRepository
    password_hasher: PasswordHasher
    
    async def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        # Verificar si el email ya existe
        email = Email(dto.email)
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Verificar si el username ya existe
        existing_user = await self.user_repository.find_by_username(dto.username)
        if existing_user:
            raise ValueError("Username already taken")
        
        # Crear nueva entidad User
        user = User(
            id=UserId(str(uuid.uuid4())),
            email=email,
            username=dto.username,
            hashed_password=HashedPassword(
                self.password_hasher.hash(dto.password)
            ),
            full_name=dto.full_name
        )
        
        # Guardar en repositorio
        saved_user = await self.user_repository.create(user)
        
        # Retornar DTO de respuesta
        return UserResponseDTO.from_entity(saved_user)
USECASE

# 5. DTOs
cat > auth-service/src/application/dto/user_dto.py << 'DTO'
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ...domain.entities.user import User

@dataclass
class CreateUserDTO:
    """DTO para crear usuario"""
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

@dataclass
class UserResponseDTO:
    """DTO de respuesta de usuario"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserResponseDTO':
        return cls(
            id=user.id,
            email=str(user.email),
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at
        )
DTO

# 6. INFRASTRUCTURE - MongoDB Implementation
cat > auth-service/src/infrastructure/repositories/mongodb_user_repository.py << 'MONGO'
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects import UserId, Email, HashedPassword
from datetime import datetime

class MongoDBUserRepository(UserRepository):
    """Implementación concreta del repositorio usando MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users
    
    async def create(self, user: User) -> User:
        user_dict = self._entity_to_dict(user)
        await self.collection.insert_one(user_dict)
        return user
    
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        user_dict = await self.collection.find_one({"_id": user_id})
        return self._dict_to_entity(user_dict) if user_dict else None
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        user_dict = await self.collection.find_one({"email": str(email)})
        return self._dict_to_entity(user_dict) if user_dict else None
    
    async def find_by_username(self, username: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"username": username})
        return self._dict_to_entity(user_dict) if user_dict else None
    
    async def update(self, user: User) -> User:
        user_dict = self._entity_to_dict(user)
        await self.collection.replace_one({"_id": user.id}, user_dict)
        return user
    
    async def delete(self, user_id: UserId) -> bool:
        result = await self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for user_dict in cursor:
            users.append(self._dict_to_entity(user_dict))
        return users
    
    def _entity_to_dict(self, user: User) -> dict:
        return {
            "_id": user.id,
            "email": str(user.email),
            "username": user.username,
            "hashed_password": user.hashed_password,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    
    def _dict_to_entity(self, data: dict) -> User:
        return User(
            id=UserId(data["_id"]),
            email=Email(data["email"]),
            username=data["username"],
            hashed_password=HashedPassword(data["hashed_password"]),
            full_name=data.get("full_name"),
            is_active=data.get("is_active", True),
            is_superuser=data.get("is_superuser", False),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow())
        )
MONGO

echo "✅ Clean Architecture implementada en auth-service"
