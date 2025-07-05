from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.configuration import Configuration, ConfigurationHistory
from decimal import Decimal

class ConfigurationRepository:
    """Repositorio para configuraciones del sistema"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.configurations
        self.history_collection = database.configuration_history
    
    async def create(self, config: Configuration) -> Configuration:
        """Crea una nueva configuración"""
        config_dict = config.dict(exclude={'id'})
        config_dict['created_at'] = datetime.utcnow()
        config_dict['updated_at'] = None
        
        result = await self.collection.insert_one(config_dict)
        config.id = str(result.inserted_id)
        return config
    
    async def get_by_id(self, config_id: str) -> Optional[Configuration]:
        """Obtiene configuración por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(config_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Configuration(**doc)
        except Exception:
            return None
        return None
    
    async def get_by_key(self, key: str) -> Optional[Configuration]:
        """Obtiene configuración por clave"""
        doc = await self.collection.find_one({"key": key})
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            return Configuration(**doc)
        return None
    
    async def get_all(self, category: Optional[str] = None) -> List[Configuration]:
        """Obtiene todas las configuraciones, opcionalmente por categoría"""
        filter_dict = {}
        if category:
            filter_dict['category'] = category
        
        cursor = self.collection.find(filter_dict)
        configs = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            configs.append(Configuration(**doc))
        
        return configs
    
    async def get_active_configs(self) -> List[Configuration]:
        """Obtiene solo configuraciones activas"""
        cursor = self.collection.find({"is_active": True})
        configs = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            configs.append(Configuration(**doc))
        
        return configs
    
    async def update(self, config: Configuration) -> Configuration:
        """Actualiza una configuración"""
        config_dict = config.dict(exclude={'id'})
        config_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(config.id)},
            {"$set": config_dict}
        )
        
        return config
    
    async def save_history(self, history: ConfigurationHistory) -> ConfigurationHistory:
        """Guarda un registro de histórico"""
        history_dict = history.dict(exclude={'id'})
        result = await self.history_collection.insert_one(history_dict)
        history.id = str(result.inserted_id)
        return history
    
    async def get_history(self, config_id: str) -> List[ConfigurationHistory]:
        """Obtiene el histórico de una configuración"""
        cursor = self.history_collection.find(
            {"configuration_id": config_id}
        ).sort("changed_at", -1)
        
        history = []
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            history.append(ConfigurationHistory(**doc))
        
        return history
    
    async def get_quantity_discounts(self) -> Dict[int, Decimal]:
        """Obtiene descuentos por cantidad desde configuraciones"""
        # Buscar configuraciones de descuentos
        cursor = self.collection.find({"category": "descuentos_cantidad"})
        discounts = {}
        
        async for doc in cursor:
            if doc['key'].startswith('descuento_'):
                try:
                    # Extraer cantidad del key (ej: descuento_10, descuento_50)
                    cantidad = int(doc['key'].split('_')[1])
                    porcentaje = Decimal(doc['value'])
                    discounts[cantidad] = porcentaje
                except (ValueError, IndexError):
                    continue
        
        return discounts
