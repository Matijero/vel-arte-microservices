from decimal import Decimal, ROUND_UP
from typing import Dict, List
import math
from ..entities.molde import Molde
from ..entities.producto import Producto
from ..value_objects.calculation_params import CalculationParams, CostBreakdown
from datetime import datetime

class CostCalculationService:
    """Servicio de dominio para cálculos de costos de productos"""
    
    def calculate_product_cost(
        self, 
        molde: Molde, 
        producto: Producto,
        params: CalculationParams,
        cantidad_gotas: int = 0
    ) -> CostBreakdown:
        """Calcula el costo completo de un producto siguiendo las reglas de negocio"""
        
        # 1. Cálculo de cera
        peso_cera_kg = molde.peso_figura / 1000
        costo_cera = peso_cera_kg * params.valor_cera_kg
        
        # 2. Cálculo de aditivo
        gramos_aditivo = molde.peso_figura * (params.porc_aditivo / 100)
        costo_aditivo = (gramos_aditivo / 1000) * params.valor_aditivo_kg
        
        # 3. Cálculo de fragancia
        gramos_fragancia = molde.peso_figura * (params.porc_fragancia / 100)
        ml_fragancia = gramos_fragancia  # Aproximación 1g = 1ml
        costo_fragancia = ml_fragancia * params.valor_fragancia_ml
        
        # 4. Cálculo de colorante
        costo_colorante = Decimal(cantidad_gotas) * params.valor_colorante_gota
        
        # 5. Cálculo de pabilo
        costo_pabilo = molde.longitud_pabilo * params.valor_pabilo_metro
        
        # 6. Otros insumos (por ahora 0, se puede extender)
        costo_otros_insumos = Decimal('0')
        
        # 7. Costo base total
        costo_base = (
            costo_cera + costo_aditivo + costo_fragancia + 
            costo_colorante + costo_pabilo + costo_otros_insumos
        )
        
        # 8. Aplicar ganancia y detalle
        # Usar margen custom del producto o el general
        porc_ganancia_final = (
            producto.margen_ganancia_custom or params.porc_ganancia
        )
        porc_detalle_final = (
            producto.porcentaje_detalle_custom or 
            self._get_detalle_by_complejidad(molde.complejidad, params.porc_detalle)
        )
        
        costo_ganancia = costo_base * (porc_ganancia_final / 100)
        costo_detalle = costo_base * (porc_detalle_final / 100)
        subtotal_sin_admin = costo_base + costo_ganancia + costo_detalle
        
        # 9. Gastos administrativos
        gastos_admin = subtotal_sin_admin * (params.porc_admin / 100)
        subtotal_con_admin = subtotal_sin_admin + gastos_admin
        
        # 10. Redondeo
        valor_redondeado = self._redondear_al_multiplo(
            subtotal_con_admin, params.multiplo_redondeo
        )
        
        # 11. Calcular descuentos aplicables
        descuentos_aplicables = {}
        for cantidad, porcentaje in params.descuentos_cantidad.items():
            precio_con_descuento = valor_redondeado * (1 - porcentaje / 100)
            descuentos_aplicables[cantidad] = precio_con_descuento
        
        return CostBreakdown(
            costo_cera=costo_cera,
            costo_aditivo=costo_aditivo,
            costo_fragancia=costo_fragancia,
            costo_colorante=costo_colorante,
            costo_pabilo=costo_pabilo,
            costo_otros_insumos=costo_otros_insumos,
            costo_base=costo_base,
            costo_ganancia=costo_ganancia,
            costo_detalle=costo_detalle,
            subtotal_sin_admin=subtotal_sin_admin,
            gastos_admin=gastos_admin,
            subtotal_con_admin=subtotal_con_admin,
            valor_redondeado=valor_redondeado,
            descuentos_aplicables=descuentos_aplicables,
            fecha_calculo=datetime.utcnow(),
            parametros_usados=params
        )
    
    def _get_detalle_by_complejidad(self, complejidad: str, base_detalle: Decimal) -> Decimal:
        """Ajusta el porcentaje de detalle según complejidad"""
        multipliers = {
            "simple": Decimal('1.0'),
            "intermedio": Decimal('1.5'),
            "complejo": Decimal('2.0')
        }
        return base_detalle * multipliers.get(complejidad, Decimal('1.0'))
    
    def _redondear_al_multiplo(self, valor: Decimal, multiplo: int) -> Decimal:
        """Redondea hacia arriba al múltiplo especificado"""
        return Decimal(math.ceil(float(valor) / multiplo) * multiplo)
    
    def calculate_bulk_discount(
        self, 
        precio_unitario: Decimal, 
        cantidad: int,
        descuentos: Dict[int, Decimal]
    ) -> Decimal:
        """Calcula el descuento por cantidad"""
        descuento_aplicable = Decimal('0')
        
        # Encontrar el descuento más alto aplicable
        for min_cantidad, porcentaje in sorted(descuentos.items()):
            if cantidad >= min_cantidad:
                descuento_aplicable = porcentaje
        
        return precio_unitario * (1 - descuento_aplicable / 100)
    
    def validate_calculation_params(self, params: CalculationParams) -> List[str]:
        """Valida que los parámetros de cálculo sean válidos"""
        errors = []
        
        # Validar porcentajes
        if not (0 <= params.porc_aditivo <= 50):
            errors.append("Porcentaje de aditivo debe estar entre 0% y 50%")
        
        if not (0 <= params.porc_fragancia <= 30):
            errors.append("Porcentaje de fragancia debe estar entre 0% y 30%")
        
        if not (1 <= params.porc_ganancia <= 500):
            errors.append("Porcentaje de ganancia debe estar entre 1% y 500%")
        
        # Validar precios
        if params.valor_cera_kg <= 0:
            errors.append("Valor de cera por kg debe ser mayor a 0")
        
        if params.multiplo_redondeo <= 0:
            errors.append("Múltiplo de redondeo debe ser mayor a 0")
        
        return errors
