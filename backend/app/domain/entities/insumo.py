from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Insumo(BaseModel):
    """
    Modelo para los insumos - basado en tu hoja Excel 'Insumos'
    Campos: CODIGO, CAPACIDAD, DESCRIPCION, COSTO, IMPUESTO, CANTIDAD, ENVIO, VALOR TOTAL, PROVEEDOR, FECHA
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    codigo: str = Field(..., description="Código único del insumo (ej: CH001, VH001)")
    capacidad: Optional[str] = Field(None, description="Capacidad del insumo (ej: 45 ML)")
    descripcion: str = Field(..., description="Descripción del insumo")
    costo: Decimal = Field(..., description="Costo unitario")
    impuesto: Decimal = Field(default=Decimal("0"), description="Impuesto (generalmente 10%)")
    cantidad: int = Field(default=1, description="Cantidad en inventario")
    envio: Decimal = Field(default=Decimal("0"), description="Costo de envío")
    valor_total: Optional[Decimal] = Field(None, description="Valor total calculado")
    proveedor: Optional[str] = Field(None, description="Nombre del proveedor")
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    activo: bool = Field(default=True, description="Si el insumo está activo")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, Decimal: str}

class InsumoCreate(BaseModel):
    """Esquema para crear un nuevo insumo"""
    codigo: str
    capacidad: Optional[str] = None
    descripcion: str
    costo: Decimal
    impuesto: Optional[Decimal] = None
    cantidad: int = 1
    envio: Optional[Decimal] = None
    proveedor: Optional[str] = None

class InsumoUpdate(BaseModel):
    """Esquema para actualizar un insumo"""
    capacidad: Optional[str] = None
    descripcion: Optional[str] = None
    costo: Optional[Decimal] = None
    impuesto: Optional[Decimal] = None
    cantidad: Optional[int] = None
    envio: Optional[Decimal] = None
    proveedor: Optional[str] = None
    activo: Optional[bool] = None

class InsumoResponse(BaseModel):
    """Esquema para respuesta con insumo"""
    id: str
    codigo: str
    capacidad: Optional[str]
    descripcion: str
    costo: str  # Como string para evitar problemas de serialización
    impuesto: str
    cantidad: int
    envio: str
    valor_total: Optional[str]
    proveedor: Optional[str]
    fecha_actualizacion: datetime
    activo: bool
