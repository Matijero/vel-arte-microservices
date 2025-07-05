from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models.user import UserCreate, UserLogin, Token, UserResponse
from src.services.auth_service import AuthService
from datetime import timedelta
import jwt
from src.core.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    user_data = user.dict()
    created_user = await AuthService.create_user(user_data)
    return UserResponse(**created_user)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await AuthService.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@router.get("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        return {"username": username, "role": role, "valid": True}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
