from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    client: AsyncIOMotorClient = None
    database = None

db = DatabaseConnection()

async def connect_to_mongo():
    """Conectar a MongoDB usando configuración del .env"""
    try:
        logger.info(f"Conectando a MongoDB: {settings.mongodb_url}")
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Verificar conexión
        await db.client.admin.command('ping')
        logger.info(f"✅ Conectado a la base de datos: {settings.database_name}")
        
    except Exception as e:
        logger.error(f"❌ Error conectando a MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    if db.client:
        db.client.close()
        logger.info("Conexión a MongoDB cerrada")

def get_database():
    return db.database
