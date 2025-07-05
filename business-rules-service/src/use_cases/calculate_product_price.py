from typing import Dict, Optional
from decimal import Decimal
from ..domain.services.cost_calculation_service import CostCalculationService
from ..domain.services.configuration_service import ConfigurationService
from ..domain.entities.producto import Producto, ProductoCalculado
from ..domain.entities.molde import Molde

class CalculateProductPriceUseCase:
    """Caso de uso para calcular precio de un producto"""
    
    def __init__(
        self, 
        calculation_service: CostCalculationService,
        configuration_service: ConfigurationService,
        molde_repository,
        producto_repository
    ):
        self.calculation_service = calculation_service
        self.configuration_service = configuration_service
        self.molde_repository = molde_repository
        self.producto_repository = producto_repository
    
    async def execute(
        self, 
        producto_id: str, 
        cantidad_gotas: int = 0,
        custom_params: Optional[Dict] = None
    ) -> ProductoCalculado:
        """Ejecuta el cálculo completo de precio para un producto"""
        
        # 1. Obtener producto y molde
        producto = await self.producto_repository.get_by_id(producto_id)
        if not producto:
            raise ValueError(f"Producto {producto_id} no encontrado")
        
        molde = await self.molde_repository.get_by_id(producto.molde_id)
        if not molde:
            raise ValueError(f"Molde {producto.molde_id} no encontrado")
        
        # 2. Obtener parámetros de cálculo
        if custom_params:
            # Usar parámetros personalizados (para simulaciones)
            params = self._build_custom_params(custom_params)
        else:
            # Usar parámetros del sistema
            params = await self.configuration_service.get_calculation_params()
        
        # 3. Validar parámetros
        validation_errors = self.calculation_service.validate_calculation_params(params)
        if validation_errors:
            raise ValueError(f"Parámetros inválidos: {', '.join(validation_errors)}")
        
        # 4. Calcular costos
        if 'cantidad_gotas' in producto.color_config:
            cantidad_gotas = producto.color_config['cantidad_gotas']
        
        cost_breakdown = self.calculation_service.calculate_product_cost(
            molde=molde,
            producto=producto,
            params=params,
            cantidad_gotas=cantidad_gotas
        )
        
        # 5. Preparar respuesta
        desglose_detallado = {
            "costos_base": {
                "cera": float(cost_breakdown.costo_cera),
                "aditivo": float(cost_breakdown.costo_aditivo),
                "fragancia": float(cost_breakdown.costo_fragancia),
                "colorante": float(cost_breakdown.costo_colorante),
                "pabilo": float(cost_breakdown.costo_pabilo),
                "otros": float(cost_breakdown.costo_otros_insumos),
                "total_base": float(cost_breakdown.costo_base)
            },
            "aplicaciones": {
                "ganancia": float(cost_breakdown.costo_ganancia),
                "detalle": float(cost_breakdown.costo_detalle),
                "administracion": float(cost_breakdown.gastos_admin)
            },
            "subtotales": {
                "sin_admin": float(cost_breakdown.subtotal_sin_admin),
                "con_admin": float(cost_breakdown.subtotal_con_admin),
                "redondeado": float(cost_breakdown.valor_redondeado)
            },
            "descuentos_por_cantidad": {
                str(k): float(v) for k, v in cost_breakdown.descuentos_aplicables.items()
            },
            "parametros_utilizados": {
                "porc_aditivo": float(params.porc_aditivo),
                "porc_fragancia": float(params.porc_fragancia),
                "porc_ganancia": float(params.porc_ganancia),
                "porc_detalle": float(params.porc_detalle),
                "porc_admin": float(params.porc_admin)
            }
        }
        
        # 6. Calcular ganancia neta
        ganancia_neta = cost_breakdown.valor_redondeado - cost_breakdown.costo_base
        
        return ProductoCalculado(
            producto=producto,
            desglose_detallado=desglose_detallado,
            precio_final=cost_breakdown.valor_redondeado,
            precio_con_descuentos=cost_breakdown.descuentos_aplicables,
            ganancia_neta=ganancia_neta,
            fecha_calculo=cost_breakdown.fecha_calculo
        )
    
    def _build_custom_params(self, custom_params: Dict):
        """Construye parámetros personalizados para simulaciones"""
        # Implementar lógica para parámetros custom
        pass

class RecalculateAllProductsUseCase:
    """Caso de uso para recalcular todos los productos cuando cambian configuraciones"""
    
    def __init__(
        self,
        calculate_product_use_case: CalculateProductPriceUseCase,
        producto_repository
    ):
        self.calculate_product_use_case = calculate_product_use_case
        self.producto_repository = producto_repository
    
    async def execute(self) -> Dict[str, any]:
        """Recalcula todos los productos activos"""
        
        productos = await self.producto_repository.get_active_products()
        resultados = {
            "productos_procesados": 0,
            "productos_con_error": 0,
            "errores": []
        }
        
        for producto in productos:
            try:
                resultado = await self.calculate_product_use_case.execute(producto.id)
                
                # Actualizar precio sugerido del producto
                producto.precio_sugerido = resultado.precio_final
                await self.producto_repository.update(producto)
                
                resultados["productos_procesados"] += 1
                
            except Exception as e:
                resultados["productos_con_error"] += 1
                resultados["errores"].append({
                    "producto_id": producto.id,
                    "error": str(e)
                })
        
        return resultados
