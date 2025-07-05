from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

class Producto(BaseModel):
    """Entidad Producto del catálogo"""
    id: Optional[str] = None
    molde_id: str
    nombre: str
    descripcion: Optional[str] = None
    fragancia_id: Optional[str] = None  # ID de fragancia específica
    color_config: Dict  # Configuración de colores y gotas
    categoria: str
    precio_sugerido: Optional[Decimal] = None  # Calculado automáticamente
    precio_manual: Optional[Decimal] = None   # Precio manual si existe
    margen_ganancia_custom: Optional[Decimal] = None  # Margen específico del producto
    porcentaje_detalle_custom: Optional[Decimal] = None  # % detalle específico
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Campos calculados (no almacenados, se calculan dinámicamente)
    costo_calculado: Optional[Decimal] = None
    desglose_costos: Optional[Dict] = None

class ProductoCalculado(BaseModel):
    """Resultado de cálculo completo de un producto"""
    producto: Producto
    desglose_detallado: Dict
    precio_final: Decimal
    precio_con_descuentos: Dict  # Por cantidad
    ganancia_neta: Decimal
    fecha_calculo: datetime
