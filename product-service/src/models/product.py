from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MoldeBase(BaseModel):
    nombre: str
    material: str
    peso: float
    precio_base: float
    categoria: str
    disponible: bool = True

class MoldeCreate(MoldeBase):
    pass

class MoldeResponse(MoldeBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class ProductoBase(BaseModel):
    molde_id: str
    color: str
    fragancia: str
    precio_venta: float
    costo_produccion: float

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: str
    sku: str
    created_at: datetime
