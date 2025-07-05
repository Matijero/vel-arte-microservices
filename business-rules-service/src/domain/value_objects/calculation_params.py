from pydantic import BaseModel
from decimal import Decimal
from typing import Dict, Optional

class CalculationParams(BaseModel):
    """Parámetros para cálculo de costos"""
    # Porcentajes
    porc_aditivo: Decimal
    porc_fragancia: Decimal
    porc_ganancia: Decimal
    porc_detalle: Decimal
    porc_admin: Decimal
    
    # Precios base de insumos
    valor_cera_kg: Decimal
    valor_aditivo_kg: Decimal
    valor_fragancia_ml: Decimal
    valor_colorante_gota: Decimal
    valor_pabilo_metro: Decimal
    
    # Reglas de redondeo
    multiplo_redondeo: int = 500
    
    # Descuentos por cantidad
    descuentos_cantidad: Dict[int, Decimal]  # {cantidad: porcentaje_descuento}

class CostBreakdown(BaseModel):
    """Desglose detallado de costos"""
    # Costos base
    costo_cera: Decimal
    costo_aditivo: Decimal
    costo_fragancia: Decimal
    costo_colorante: Decimal
    costo_pabilo: Decimal
    costo_otros_insumos: Decimal
    
    # Subtotales
    costo_base: Decimal
    costo_ganancia: Decimal
    costo_detalle: Decimal
    subtotal_sin_admin: Decimal
    gastos_admin: Decimal
    subtotal_con_admin: Decimal
    
    # Final
    valor_redondeado: Decimal
    descuentos_aplicables: Dict[int, Decimal]
    
    # Metadata
    fecha_calculo: datetime
    parametros_usados: CalculationParams
