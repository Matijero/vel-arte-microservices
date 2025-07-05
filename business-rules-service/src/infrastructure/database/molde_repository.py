from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.molde import Molde, MoldeInsumo

class MoldeRepository:
    """Repositorio para moldes"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.moldes
        self.molde_insumos_collection = database.molde_insumos
    
    async def create(self, molde: Molde) -> Molde:
        """Crea un nuevo molde"""
        molde_dict = molde.dict(exclude={'id'})
        molde_dict['created_at'] = datetime.utcnow()
        molde_dict['updated_at'] = None
        
        result = await self.collection.insert_one(molde_dict)
        molde.id = str(result.inserted_id)
        return molde
    
    async def get_by_id(self, molde_id: str) -> Optional[Molde]:
        """Obtiene molde por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(molde_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Molde(**doc)
        except Exception:
            return None
        return None
    
    async def get_all_active(self) -> List[Molde]:
        """Obtiene todos los moldes activos"""
        cursor = self.collection.find({"is_active": True})
        moldes = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            moldes.append(Molde(**doc))
        
        return moldes
    
    async def update(self, molde: Molde) -> Molde:
        """Actualiza un molde"""
        molde_dict = molde.dict(exclude={'id'})
        molde_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(molde.id)},
            {"$set": molde_dict}
        )
        
        return molde
    
    async def get_insumos_for_molde(self, molde_id: str) -> List[MoldeInsumo]:
        """Obtiene los insumos requeridos para un molde"""
        cursor = self.molde_insumos_collection.find({"molde_id": molde_id})
        insumos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            insumos.append(MoldeInsumo(**doc))
        
        return insumos
