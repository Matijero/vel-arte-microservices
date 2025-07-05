from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vel Arte Auth Service",
    description="Servicio de autenticación para Vel Arte",
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

# Incluir rutas (importar aquí para evitar errores circulares)
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
        "service": "auth-service",
        "database": os.getenv("DATABASE_NAME", "vel_arte_auth"),
        "secret_key_loaded": bool(os.getenv("SECRET_KEY"))
    }

@app.get("/")
async def root():
    return {
        "message": "Vel Arte Auth Service", 
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
