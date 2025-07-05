from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vel Arte Product Service",
    description="Servicio de productos para Vel Arte",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas si existen
try:
    from src.api.routes import router
    app.include_router(router, prefix="/api/v1")
    logger.info("✅ Rutas de API cargadas correctamente")
except ImportError as e:
    logger.warning(f"⚠️ No se pudieron cargar las rutas: {e}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "product-service",
        "database": os.getenv("DATABASE_NAME", "vel_arte_products"),
        "auth_service": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
    }

@app.get("/")
async def root():
    return {
        "message": "Vel Arte Product Service", 
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
