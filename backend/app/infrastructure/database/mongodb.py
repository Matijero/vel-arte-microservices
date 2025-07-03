from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

    @classmethod
    async def connect_to_mongo(cls):
        """Crear conexión a MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(settings.database_url)
            cls.database = cls.client[settings.database_name]
            
            # Verificar conexión
            await cls.client.admin.command('ping')
            logger.info(f"✅ Conexión a MongoDB establecida - Base de datos: {settings.database_name}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        """Cerrar conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("🔒 Conexión a MongoDB cerrada")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Obtener instancia de la base de datos"""
        return cls.database

# Instancia global
database = MongoDB()
