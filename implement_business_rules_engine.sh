#!/bin/bash
echo "⚙️ IMPLEMENTANDO MOTOR DE CÁLCULOS REAL"

# Crear motor de cálculos
cat > business-rules-service/src/domain/services/calculation_engine.py << 'ENGINE'
from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
import math

@dataclass
class CalculationParameters:
    """Parámetros para el cálculo"""
    cera_gramos: Decimal
    fragancia_porcentaje: Decimal = Decimal("6")
    aditivo_porcentaje: Decimal = Decimal("8")
    colorante_gotas: int = 3
    pabilo_cm: Decimal = Decimal("15")
    cantidad_unidades: int = 1
    
@dataclass
class PriceConfiguration:
    """Configuración de precios"""
    cera_kg: Decimal = Decimal("15000")
    fragancia_ml: Decimal = Decimal("150")
    aditivo_kg: Decimal = Decimal("8000")
    colorante_gota: Decimal = Decimal("50")
    pabilo_metro: Decimal = Decimal("200")
    
@dataclass
class Percentages:
    """Porcentajes de cálculo"""
    ganancia: Decimal = Decimal("250")
    detalle: Decimal = Decimal("20")
    admin: Decimal = Decimal("10")

class CalculationEngine:
    """Motor de cálculos principal"""
    
    def __init__(self, prices: PriceConfiguration, percentages: Percentages):
        self.prices = prices
        self.percentages = percentages
        self.descuentos = {
            10: Decimal("5"),   # 5% descuento para 10+ unidades
            20: Decimal("10"),  # 10% descuento para 20+ unidades
            50: Decimal("15"),  # 15% descuento para 50+ unidades
        }
    
    def calculate_quote(self, params: CalculationParameters) -> Dict:
        """Calcular cotización completa"""
        
        # 1. Calcular costos de materiales
        costo_cera = (params.cera_gramos / 1000) * self.prices.cera_kg
        
        fragancia_ml = params.cera_gramos * (params.fragancia_porcentaje / 100)
        costo_fragancia = fragancia_ml * (self.prices.fragancia_ml / 1000)
        
        aditivo_gramos = params.cera_gramos * (params.aditivo_porcentaje / 100)
        costo_aditivo = (aditivo_gramos / 1000) * self.prices.aditivo_kg
        
        costo_colorante = params.colorante_gotas * self.prices.colorante_gota
        costo_pabilo = (params.pabilo_cm / 100) * self.prices.pabilo_metro
        
        # 2. Costo total materiales
        costo_materiales = (
            costo_cera + costo_fragancia + costo_aditivo + 
            costo_colorante + costo_pabilo
        )
        
        # 3. Aplicar porcentajes
        costo_con_ganancia = costo_materiales * (1 + self.percentages.ganancia / 100)
        costo_con_detalle = costo_con_ganancia * (1 + self.percentages.detalle / 100)
        precio_unitario = costo_con_detalle * (1 + self.percentages.admin / 100)
        
        # 4. Redondear a múltiplo de 500
        precio_unitario_redondeado = self._redondear_precio(precio_unitario)
        
        # 5. Calcular precio total con descuento
        precio_total = precio_unitario_redondeado * params.cantidad_unidades
        descuento = self._calcular_descuento(params.cantidad_unidades)
        precio_con_descuento = precio_total * (1 - descuento / 100)
        
        return {
            "detalle_costos": {
                "cera": float(costo_cera),
                "fragancia": float(costo_fragancia),
                "aditivo": float(costo_aditivo),
                "colorante": float(costo_colorante),
                "pabilo": float(costo_pabilo),
                "total_materiales": float(costo_materiales)
            },
            "calculos": {
                "costo_con_ganancia": float(costo_con_ganancia),
                "costo_con_detalle": float(costo_con_detalle),
                "precio_unitario": float(precio_unitario),
                "precio_unitario_redondeado": float(precio_unitario_redondeado)
            },
            "totales": {
                "cantidad": params.cantidad_unidades,
                "precio_total": float(precio_total),
                "descuento_porcentaje": float(descuento),
                "descuento_valor": float(precio_total - precio_con_descuento),
                "precio_final": float(precio_con_descuento)
            },
            "parametros_usados": {
                "fragancia_porcentaje": float(params.fragancia_porcentaje),
                "aditivo_porcentaje": float(params.aditivo_porcentaje),
                "ganancia_porcentaje": float(self.percentages.ganancia),
                "detalle_porcentaje": float(self.percentages.detalle),
                "admin_porcentaje": float(self.percentages.admin)
            }
        }
    
    def _redondear_precio(self, precio: Decimal, multiplo: int = 500) -> Decimal:
        """Redondear precio al múltiplo más cercano"""
        return Decimal(math.ceil(float(precio) / multiplo) * multiplo)
    
    def _calcular_descuento(self, cantidad: int) -> Decimal:
        """Calcular descuento por cantidad"""
        for min_cantidad, descuento in sorted(self.descuentos.items(), reverse=True):
            if cantidad >= min_cantidad:
                return descuento
        return Decimal("0")
ENGINE

echo "✅ Motor de cálculos implementado"
