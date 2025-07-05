from typing import List, Optional
from src.database.mongodb import get_database
from src.models.product import MoldeCreate, MoldeResponse, ProductoCreate, ProductoResponse
from datetime import datetime
from bson import ObjectId
import uuid

class ProductService:
    
    @staticmethod
    async def create_molde(molde_data: MoldeCreate) -> MoldeResponse:
        db = await get_database()
        
        molde_dict = molde_data.dict()
        molde_dict["created_at"] = datetime.utcnow()
        
        result = await db.moldes.insert_one(molde_dict)
        molde_dict["id"] = str(result.inserted_id)
        
        return MoldeResponse(**molde_dict)
    
    @staticmethod
    async def get_moldes() -> List[MoldeResponse]:
        db = await get_database()
        moldes_cursor = db.moldes.find({"disponible": True})
        moldes = []
        
        async for molde in moldes_cursor:
            molde["id"] = str(molde["_id"])
            moldes.append(MoldeResponse(**molde))
        
        return moldes
    
    @staticmethod
    async def get_molde_by_id(molde_id: str) -> Optional[MoldeResponse]:
        db = await get_database()
        molde = await db.moldes.find_one({"_id": ObjectId(molde_id)})
        
        if molde:
            molde["id"] = str(molde["_id"])
            return MoldeResponse(**molde)
        return None
    
    @staticmethod
    async def create_producto(producto_data: ProductoCreate) -> ProductoResponse:
        db = await get_database()
        
        producto_dict = producto_data.dict()
        producto_dict["sku"] = f"VEL-{uuid.uuid4().hex[:8].upper()}"
        producto_dict["created_at"] = datetime.utcnow()
        
        result = await db.productos.insert_one(producto_dict)
        producto_dict["id"] = str(result.inserted_id)
        
        return ProductoResponse(**producto_dict)
