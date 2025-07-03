from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones a MongoDB"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.database: AsyncIOMotorDatabase = None
        self.connected = False
    
    async def connect(self, database_url: str = "mongodb://localhost:27017/", database_name: str = "velas_db"):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(database_url)
            self.database = self.client[database_name]
            
            # Verificar conexión
            await self.client.admin.command('ping')
            self.connected = True
            logger.info(f"✅ Conectado a MongoDB: {database_name}")
            
            # Crear índices
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Crear índices para optimizar consultas"""
        try:
            # Índices para insumos
            await self.database.insumos.create_index("codigo", unique=True)
            await self.database.insumos.create_index("tipo")
            await self.database.insumos.create_index("activo")
            
            # Índices para moldes
            await self.database.moldes.create_index("codigo", unique=True)
            await self.database.moldes.create_index("estado")
            await self.database.moldes.create_index("lineas_compatibles")
            
            # Índices para colores
            await self.database.colores.create_index("codigo", unique=True)
            
            # Índices para productos
            await self.database.productos.create_index("codigo", unique=True)
            await self.database.productos.create_index("linea_producto")
            
            logger.info("✅ Índices de MongoDB creados")
            
        except Exception as e:
            logger.warning(f"⚠️ Error creando índices: {e}")
    
    async def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔒 Conexión a MongoDB cerrada")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Obtener instancia de la base de datos"""
        if not self.connected:
            raise RuntimeError("Base de datos no conectada")
        return self.database

# Instancia global
db_manager = DatabaseManager()

class InsumoRepository:
    """Repositorio para operaciones de insumos en MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.insumos
    
    async def crear(self, insumo_data: dict) -> dict:
        """Crear nuevo insumo"""
        insumo_data['fecha_creacion'] = datetime.now()
        insumo_data['fecha_actualizacion'] = datetime.now()
        
        result = await self.collection.insert_one(insumo_data)
        insumo_data['_id'] = str(result.inserted_id)
        return insumo_data
    
    async def obtener_por_codigo(self, codigo: str) -> Optional[dict]:
        """Obtener insumo por código"""
        insumo = await self.collection.find_one({"codigo": codigo})
        if insumo:
            insumo['_id'] = str(insumo['_id'])
        return insumo
    
    async def listar(self, filtros: dict = None) -> List[dict]:
        """Listar insumos con filtros opcionales"""
        filtros = filtros or {}
        cursor = self.collection.find(filtros)
        insumos = []
        async for insumo in cursor:
            insumo['_id'] = str(insumo['_id'])
            insumos.append(insumo)
        return insumos
    
    async def actualizar(self, codigo: str, datos_actualizar: dict) -> bool:
        """Actualizar insumo"""
        datos_actualizar['fecha_actualizacion'] = datetime.now()
        result = await self.collection.update_one(
            {"codigo": codigo}, 
            {"$set": datos_actualizar}
        )
        return result.modified_count > 0
    
    async def eliminar(self, codigo: str) -> bool:
        """Eliminar insumo"""
        result = await self.collection.delete_one({"codigo": codigo})
        return result.deleted_count > 0

class MoldeRepository:
    """Repositorio para operaciones de moldes en MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.moldes
    
    async def crear(self, molde_data: dict) -> dict:
        """Crear nuevo molde"""
        molde_data['fecha_creacion'] = datetime.now()
        molde_data['fecha_actualizacion'] = datetime.now()
        
        result = await self.collection.insert_one(molde_data)
        molde_data['_id'] = str(result.inserted_id)
        return molde_data
    
    async def obtener_por_codigo(self, codigo: str) -> Optional[dict]:
        """Obtener molde por código"""
        molde = await self.collection.find_one({"codigo": codigo})
        if molde:
            molde['_id'] = str(molde['_id'])
        return molde
    
    async def listar(self, filtros: dict = None) -> List[dict]:
        """Listar moldes con filtros opcionales"""
        filtros = filtros or {}
        cursor = self.collection.find(filtros)
        moldes = []
        async for molde in cursor:
            molde['_id'] = str(molde['_id'])
            moldes.append(molde)
        return moldes
    
    async def actualizar(self, codigo: str, datos_actualizar: dict) -> bool:
        """Actualizar molde"""
        datos_actualizar['fecha_actualizacion'] = datetime.now()
        result = await self.collection.update_one(
            {"codigo": codigo}, 
            {"$set": datos_actualizar}
        )
        return result.modified_count > 0

class ColorRepository:
    """Repositorio para operaciones de colores en MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.colores
    
    async def crear(self, color_data: dict) -> dict:
        """Crear nuevo color"""
        color_data['fecha_creacion'] = datetime.now()
        color_data['fecha_actualizacion'] = datetime.now()
        
        result = await self.collection.insert_one(color_data)
        color_data['_id'] = str(result.inserted_id)
        return color_data
    
    async def obtener_por_codigo(self, codigo: str) -> Optional[dict]:
        """Obtener color por código"""
        color = await self.collection.find_one({"codigo": codigo})
        if color:
            color['_id'] = str(color['_id'])
        return color
    
    async def listar(self) -> List[dict]:
        """Listar todos los colores"""
        cursor = self.collection.find({})
        colores = []
        async for color in cursor:
            color['_id'] = str(color['_id'])
            colores.append(color)
        return colores
