from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.infrastructure.database.mongodb import database
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema web para gestión de costos y producción de velas artesanales",
    debug=settings.debug
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Inicializar conexiones al arrancar"""
    await database.connect_to_mongo()
    logger.info("🚀 Aplicación iniciada correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Cerrar conexiones al apagar"""
    await database.close_mongo_connection()
    logger.info("🛑 Aplicación detenida")

# Ruta de prueba
@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {
        "message": "¡Bienvenido al Sistema de Gestión de Velas Vel Arte!",
        "version": settings.app_version,
        "status": "🟢 Funcionando correctamente"
    }

# Ruta de salud del sistema
@app.get("/health")
async def health_check():
    """Verificar que todo está funcionando"""
    try:
        # Verificar conexión a base de datos
        db = database.get_database()
        await db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-07-02",
            "message": "✅ Sistema funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "❌ Problema con la base de datos"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
