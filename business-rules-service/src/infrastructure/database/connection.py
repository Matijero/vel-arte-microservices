from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27018/vel_arte_db?authSource=admin")
DATABASE_NAME = "vel_arte_db"

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Conecta a MongoDB"""
    mongodb.client = AsyncIOMotorClient(MONGODB_URL)
    mongodb.database = mongodb.client[DATABASE_NAME]

async def close_mongo_connection():
    """Cierra la conexión a MongoDB"""
    mongodb.client.close()

def get_database():
    """Obtiene la instancia de la base de datos"""
    return mongodb.database
