from motor.motor_asyncio import AsyncIOMotorClient
import os

client = None
database = None

async def connect_to_mongo():
    global client, database
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@mongodb:27017/vel_arte?authSource=admin")
    client = AsyncIOMotorClient(mongodb_url)
    database = client.get_default_database()
    print(f"✅ Conectado a MongoDB: {mongodb_url}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("🔌 Desconectado de MongoDB")

async def get_database():
    return database
