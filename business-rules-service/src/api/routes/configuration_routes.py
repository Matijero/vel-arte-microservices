from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ...use_cases.manage_configurations import ManageConfigurationsUseCase
from ...domain.entities.configuration import Configuration, ConfigurationHistory
from ...infrastructure.database.configuration_repository import ConfigurationRepository
from ...domain.services.configuration_service import ConfigurationService
from ...infrastructure.database.connection import get_database

router = APIRouter(prefix="/configurations", tags=["configurations"])

def get_configuration_use_case():
    db = get_database()
    config_repo = ConfigurationRepository(db)
    config_service = ConfigurationService(config_repo)
    return ManageConfigurationsUseCase(config_service)

@router.get("/", response_model=List[Configuration])
async def get_configurations(
    category: Optional[str] = Query(None),
    use_case: ManageConfigurationsUseCase = Depends(get_configuration_use_case)
):
    """Obtiene todas las configuraciones, opcionalmente por categoría"""
    return await use_case.get_all_configurations(category)

@router.put("/{key}")
async def update_configuration(
    key: str,
    new_value: str,
    user_id: str,
    reason: Optional[str] = None,
    use_case: ManageConfigurationsUseCase = Depends(get_configuration_use_case)
):
    """Actualiza una configuración"""
    try:
        # Validar primero
        errors = await use_case.validate_configuration_change(key, new_value)
        if errors:
            raise HTTPException(status_code=400, detail=errors)
        
        # Actualizar
        config = await use_case.update_configuration(key, new_value, user_id, reason)
        return {"message": "Configuración actualizada", "configuration": config}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{key}/history", response_model=List[ConfigurationHistory])
async def get_configuration_history(
    key: str,
    use_case: ManageConfigurationsUseCase = Depends(get_configuration_use_case)
):
    """Obtiene el histórico de cambios de una configuración"""
    return await use_case.get_configuration_history(key)

@router.post("/initialize")
async def initialize_default_configurations(
    use_case: ManageConfigurationsUseCase = Depends(get_configuration_use_case)
):
    """Inicializa las configuraciones por defecto del sistema"""
    configs = await use_case.initialize_default_configurations()
    return {
        "message": f"{len(configs)} configuraciones por defecto creadas",
        "configurations": configs
    }

@router.post("/validate")
async def validate_configuration_value(
    key: str,
    value: str,
    use_case: ManageConfigurationsUseCase = Depends(get_configuration_use_case)
):
    """Valida un valor para una configuración sin guardarlo"""
    errors = await use_case.validate_configuration_change(key, value)
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
