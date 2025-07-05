from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

class ConfigurationType(str, Enum):
    PERCENTAGE = "percentage"
    PRICE = "price"
    MULTIPLIER = "multiplier"
    BOOLEAN = "boolean"
    TEXT = "text"

class Configuration(BaseModel):
    """Entidad para configuraciones dinámicas del sistema"""
    id: Optional[str] = None
    key: str  # ej: "porc_aditivo", "valor_cera_kg"
    name: str  # Nombre legible
    description: str
    value: str  # Almacenado como string, convertido según type
    type: ConfigurationType
    category: str  # "costos", "porcentajes", "redondeo", etc.
    is_active: bool = True
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    @validator('value')
    def validate_value(cls, v, values):
        if 'type' not in values:
            return v
            
        config_type = values['type']
        try:
            if config_type == ConfigurationType.PERCENTAGE:
                val = Decimal(v)
                if val < 0 or val > 100:
                    raise ValueError("Porcentaje debe estar entre 0 y 100")
            elif config_type == ConfigurationType.PRICE:
                val = Decimal(v)
                if val < 0:
                    raise ValueError("Precio no puede ser negativo")
            elif config_type == ConfigurationType.MULTIPLIER:
                val = Decimal(v)
                if val <= 0:
                    raise ValueError("Multiplicador debe ser mayor a 0")
            elif config_type == ConfigurationType.BOOLEAN:
                if v.lower() not in ['true', 'false', '1', '0']:
                    raise ValueError("Valor booleano inválido")
        except ValueError as e:
            raise ValueError(f"Valor inválido para tipo {config_type}: {e}")
        
        return v
    
    def get_decimal_value(self) -> Decimal:
        """Convierte el valor a Decimal"""
        return Decimal(self.value)
    
    def get_boolean_value(self) -> bool:
        """Convierte el valor a boolean"""
        return self.value.lower() in ['true', '1']

class ConfigurationHistory(BaseModel):
    """Histórico de cambios en configuraciones"""
    id: Optional[str] = None
    configuration_id: str
    old_value: str
    new_value: str
    changed_by: str
    changed_at: datetime
    reason: Optional[str] = None
