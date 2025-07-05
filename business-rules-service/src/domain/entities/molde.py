from pydantic import BaseModel, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class Molde(BaseModel):
    """Entidad Molde con datos técnicos para cálculos"""
    id: Optional[str] = None
    nombre: str
    codigo: str  # Código único
    peso_figura: Decimal  # Peso final en gramos
    longitud_pabilo: Decimal  # Longitud en metros
    complejidad: str  # "simple", "intermedio", "complejo"
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('peso_figura', 'longitud_pabilo')
    def validate_positive_values(cls, v):
        if v <= 0:
            raise ValueError("Los valores deben ser mayores a cero")
        return v
    
    @validator('complejidad')
    def validate_complejidad(cls, v):
        valid_values = ["simple", "intermedio", "complejo"]
        if v.lower() not in valid_values:
            raise ValueError(f"Complejidad debe ser uno de: {valid_values}")
        return v.lower()

class MoldeInsumo(BaseModel):
    """Relación entre molde e insumos específicos"""
    id: Optional[str] = None
    molde_id: str
    insumo_id: str
    cantidad_base: Decimal  # Cantidad base requerida
    unidad: str  # "gramos", "ml", "gotas", "metros"
    es_opcional: bool = False
