from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.producto import Producto

class ProductoRepository:
    """Repositorio para productos del catálogo"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.productos
    
    async def create(self, producto: Producto) -> Producto:
        """Crea un nuevo producto"""
        producto_dict = producto.dict(exclude={'id', 'costo_calculado', 'desglose_costos'})
        producto_dict['created_at'] = datetime.utcnow()
        producto_dict['updated_at'] = None
        
        result = await self.collection.insert_one(producto_dict)
        producto.id = str(result.inserted_id)
        return producto
    
    async def get_by_id(self, producto_id: str) -> Optional[Producto]:
        """Obtiene producto por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(producto_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Producto(**doc)
        except Exception:
            return None
        return None
    
    async def get_active_products(self) -> List[Producto]:
        """Obtiene todos los productos activos"""
        cursor = self.collection.find({"is_active": True})
        productos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            productos.append(Producto(**doc))
        
        return productos
    
    async def update(self, producto: Producto) -> Producto:
        """Actualiza un producto"""
        producto_dict = producto.dict(exclude={'id', 'costo_calculado', 'desglose_costos'})
        producto_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(producto.id)},
            {"$set": producto_dict}
        )
        
        return producto
    
    async def get_by_category(self, categoria: str) -> List[Producto]:
        """Obtiene productos por categoría"""
        cursor = self.collection.find({"categoria": categoria, "is_active": True})
        productos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            productos.append(Producto(**doc))
        
        return productos
