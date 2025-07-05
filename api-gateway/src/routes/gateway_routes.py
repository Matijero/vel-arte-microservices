from fastapi import APIRouter, Request, HTTPException
import httpx
from typing import Any
import json

router = APIRouter()

# Configuración de servicios
SERVICES = {
    "auth": "http://auth-service:8000",
    "products": "http://product-service:8000", 
    "inventory": "http://inventory-service:8000",
    "pricing": "http://pricing-service:8000",
    "analytics": "http://analytics-service:8000",
    "files": "http://file-service:8000",
    "notifications": "http://notification-service:8000"
}

async def proxy_request(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Servicio {service} no encontrado")
    
    service_url = SERVICES[service]
    target_url = f"{service_url}/{path}"
    
    # Obtener headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remover host header
    
    # Obtener body si existe
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params
        )
    
    return response

# Rutas de autenticación
@router.post("/auth/login")
@router.post("/auth/register")
@router.get("/auth/verify")
async def auth_proxy(request: Request):
    path = request.url.path.replace("/auth/", "auth/")
    response = await proxy_request("auth", path, request)
    return response.json()

# Rutas de productos
@router.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def products_proxy(path: str, request: Request):
    response = await proxy_request("products", f"products/{path}", request)
    return response.json()

@router.api_route("/moldes", methods=["GET", "POST"])
@router.api_route("/moldes/{molde_id}", methods=["GET", "PUT", "DELETE"])
async def moldes_proxy(request: Request, molde_id: str = None):
    if molde_id:
        path = f"products/moldes/{molde_id}"
    else:
        path = "products/moldes"
    
    response = await proxy_request("products", path, request)
    return response.json()
