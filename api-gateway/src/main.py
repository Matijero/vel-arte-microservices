from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Optional, Dict, Any

app = FastAPI(title="Vel Arte API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los microservicios
AUTH_SERVICE_URL = "http://auth-service:8000"
PRODUCT_SERVICE_URL = "http://product-service:8001"
BUSINESS_RULES_SERVICE_URL = "http://business-rules-service:8003"

async def forward_request(
    service_url: str, 
    path: str, 
    method: str = "GET", 
    headers: Optional[Dict] = None,
    **kwargs
):
    """Reenvía peticiones a los microservicios"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method, 
                f"{service_url}{path}", 
                headers=headers,
                **kwargs
            )
            
            if response.status_code >= 400:
                return {"error": response.text, "status_code": response.status_code}
            
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# Health check mejorado
@app.get("/health")
async def health_check():
    services_status = {}
    
    services = [
        ("auth-service", AUTH_SERVICE_URL),
        ("product-service", PRODUCT_SERVICE_URL),
        ("business-rules-service", BUSINESS_RULES_SERVICE_URL)
    ]
    
    for service_name, service_url in services:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status[service_name] = "unhealthy"
    
    overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": services_status,
        "gateway": "operational",
        "version": "2.0.0"
    }

# === AUTH ROUTES ===
@app.post("/auth/register")
async def register(request: Request):
    body = await request.json()
    return await forward_request(AUTH_SERVICE_URL, "/auth/register", "POST", json=body)

@app.post("/auth/login")
async def login(request: Request):
    body = await request.json()
    return await forward_request(AUTH_SERVICE_URL, "/auth/login", "POST", json=body)

@app.get("/auth/me")
async def get_current_user(request: Request):
    headers = dict(request.headers)
    return await forward_request(AUTH_SERVICE_URL, "/auth/me", "GET", headers=headers)

# === PRODUCT ROUTES ===
@app.get("/insumos")
async def get_insumos():
    return await forward_request(PRODUCT_SERVICE_URL, "/insumos/", "GET")

@app.post("/insumos")
async def create_insumo(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    return await forward_request(PRODUCT_SERVICE_URL, "/insumos/", "POST", headers=headers, json=body)

@app.get("/insumos/{insumo_id}")
async def get_insumo(insumo_id: str):
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "GET")

@app.put("/insumos/{insumo_id}")
async def update_insumo(insumo_id: str, request: Request):
    headers = dict(request.headers)
    body = await request.json()
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "PUT", headers=headers, json=body)

@app.delete("/insumos/{insumo_id}")
async def delete_insumo(insumo_id: str, request: Request):
    headers = dict(request.headers)
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "DELETE", headers=headers)

# === BUSINESS RULES ROUTES ===

# Configuraciones
@app.get("/configurations")
async def get_configurations(category: Optional[str] = None):
    path = "/configurations"
    if category:
        path += f"?category={category}"
    return await forward_request(BUSINESS_RULES_SERVICE_URL, path, "GET")

@app.put("/configurations/{key}")
async def update_configuration(key: str, request: Request):
    body = await request.json()
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/configurations/{key}", 
        "PUT", 
        params=body
    )

@app.get("/configurations/{key}/history")
async def get_configuration_history(key: str):
    return await forward_request(BUSINESS_RULES_SERVICE_URL, f"/configurations/{key}/history", "GET")

@app.post("/configurations/initialize")
async def initialize_configurations():
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/configurations/initialize", "POST")

# Cálculos
@app.post("/calculations/product/{producto_id}")
async def calculate_product_price(producto_id: str, request: Request):
    params = request.query_params
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/calculations/product/{producto_id}", 
        "POST", 
        params=params,
        json=body if body else None
    )

@app.post("/calculations/recalculate-all")
async def recalculate_all_products(request: Request):
    headers = dict(request.headers)
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/calculations/recalculate-all", "POST", headers=headers)

@app.get("/calculations/simulation/{producto_id}")
async def simulate_price_changes(producto_id: str, request: Request):
    params = request.query_params
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/calculations/simulation/{producto_id}", 
        "GET", 
        params=params
    )

@app.get("/calculations/params")
async def get_calculation_params():
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/calculations/params", "GET")

# Legacy routes para compatibilidad
@app.get("/moldes")
async def get_moldes():
    return await forward_request(PRODUCT_SERVICE_URL, "/moldes", "GET")

@app.get("/colores")
async def get_colores():
    return await forward_request(PRODUCT_SERVICE_URL, "/colores", "GET")

@app.get("/resumen-completo")
async def get_resumen():
    return await forward_request(PRODUCT_SERVICE_URL, "/resumen-completo", "GET")

@app.get("/")
async def root():
    return {
        "message": "Vel Arte API Gateway",
        "version": "2.0.0",
        "status": "operational",
        "services": {
            "auth": "/auth/*",
            "products": "/insumos, /moldes, /colores",
            "business_rules": "/configurations, /calculations"
        },
        "documentation": "/docs"
    }
