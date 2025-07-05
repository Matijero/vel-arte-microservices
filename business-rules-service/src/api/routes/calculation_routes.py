from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict
from ...use_cases.calculate_product_price import CalculateProductPriceUseCase, RecalculateAllProductsUseCase
from ...domain.entities.producto import ProductoCalculado
from ...domain.services.cost_calculation_service import CostCalculationService
from ...domain.services.configuration_service import ConfigurationService
from ...infrastructure.database.configuration_repository import ConfigurationRepository
from ...infrastructure.database.molde_repository import MoldeRepository
from ...infrastructure.database.producto_repository import ProductoRepository
from ...infrastructure.database.connection import get_database

router = APIRouter(prefix="/calculations", tags=["calculations"])

def get_calculate_product_use_case():
    db = get_database()
    config_repo = ConfigurationRepository(db)
    molde_repo = MoldeRepository(db)
    producto_repo = ProductoRepository(db)
    
    calculation_service = CostCalculationService()
    configuration_service = ConfigurationService(config_repo)
    
    return CalculateProductPriceUseCase(
        calculation_service, 
        configuration_service, 
        molde_repo, 
        producto_repo
    )

@router.post("/product/{producto_id}", response_model=ProductoCalculado)
async def calculate_product_price(
    producto_id: str,
    cantidad_gotas: int = Query(0, description="Cantidad de gotas de colorante"),
    custom_params: Optional[Dict] = None,
    use_case: CalculateProductPriceUseCase = Depends(get_calculate_product_use_case)
):
    """Calcula el precio de un producto específico"""
    try:
        return await use_case.execute(producto_id, cantidad_gotas, custom_params)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(e)}")

@router.post("/recalculate-all")
async def recalculate_all_products(
    calculate_use_case: CalculateProductPriceUseCase = Depends(get_calculate_product_use_case)
):
    """Recalcula todos los productos activos (usar cuando cambien configuraciones)"""
    db = get_database()
    producto_repo = ProductoRepository(db)
    
    recalculate_use_case = RecalculateAllProductsUseCase(calculate_use_case, producto_repo)
    
    try:
        resultados = await recalculate_use_case.execute()
        return {
            "message": "Recálculo completado",
            "results": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en recálculo masivo: {str(e)}")

@router.get("/simulation/{producto_id}")
async def simulate_price_changes(
    producto_id: str,
    porc_ganancia: Optional[float] = Query(None, description="Simular cambio en % ganancia"),
    porc_detalle: Optional[float] = Query(None, description="Simular cambio en % detalle"),
    cantidad_gotas: int = Query(0, description="Cantidad de gotas"),
    use_case: CalculateProductPriceUseCase = Depends(get_calculate_product_use_case)
):
    """Simula cambios en parámetros sin afectar las configuraciones del sistema"""
    custom_params = {}
    
    if porc_ganancia is not None:
        custom_params['porc_ganancia'] = porc_ganancia
    if porc_detalle is not None:
        custom_params['porc_detalle'] = porc_detalle
    
    try:
        # Cálculo actual
        resultado_actual = await use_case.execute(producto_id, cantidad_gotas)
        
        # Cálculo simulado (si hay parámetros custom)
        resultado_simulado = None
        if custom_params:
            resultado_simulado = await use_case.execute(producto_id, cantidad_gotas, custom_params)
        
        return {
            "producto_id": producto_id,
            "calculo_actual": resultado_actual,
            "calculo_simulado": resultado_simulado,
            "diferencia": {
                "precio": float(resultado_simulado.precio_final - resultado_actual.precio_final) if resultado_simulado else 0,
                "ganancia": float(resultado_simulado.ganancia_neta - resultado_actual.ganancia_neta) if resultado_simulado else 0
            } if resultado_simulado else None
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@router.get("/params")
async def get_current_calculation_params():
    """Obtiene los parámetros actuales de cálculo"""
    db = get_database()
    config_repo = ConfigurationRepository(db)
    config_service = ConfigurationService(config_repo)
    
    try:
        params = await config_service.get_calculation_params()
        return {
            "parametros": {
                "porcentajes": {
                    "aditivo": float(params.porc_aditivo),
                    "fragancia": float(params.porc_fragancia),
                    "ganancia": float(params.porc_ganancia),
                    "detalle": float(params.porc_detalle),
                    "admin": float(params.porc_admin)
                },
                "precios_insumos": {
                    "cera_kg": float(params.valor_cera_kg),
                    "aditivo_kg": float(params.valor_aditivo_kg),
                    "fragancia_ml": float(params.valor_fragancia_ml),
                    "colorante_gota": float(params.valor_colorante_gota),
                    "pabilo_metro": float(params.valor_pabilo_metro)
                },
                "redondeo": {
                    "multiplo": params.multiplo_redondeo
                },
                "descuentos_cantidad": {
                    str(k): float(v) for k, v in params.descuentos_cantidad.items()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo parámetros: {str(e)}")
