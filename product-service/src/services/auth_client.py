from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from typing import Dict

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """
    Verifica el token JWT comunicándose con el servicio de autenticación
    """
    try:
        async with httpx.AsyncClient() as client:
            # Comunicarse con auth-service internamente
            response = await client.post(
                "http://auth-service:8000/verify",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Token inválido o expirado"
                )
            
            return response.json()
            
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servicio de autenticación no disponible"
        )
