from typing import List, Optional
from ..domain.entities.configuration import Configuration, ConfigurationHistory
from ..domain.services.configuration_service import ConfigurationService

class ManageConfigurationsUseCase:
    """Caso de uso para gestión de configuraciones"""
    
    def __init__(self, configuration_service: ConfigurationService):
        self.configuration_service = configuration_service
    
    async def get_all_configurations(self, category: Optional[str] = None) -> List[Configuration]:
        """Obtiene todas las configuraciones, opcionalmente filtradas por categoría"""
        return await self.configuration_service.config_repository.get_all(category)
    
    async def update_configuration(
        self, 
        key: str, 
        new_value: str, 
        user_id: str,
        reason: Optional[str] = None
    ) -> Configuration:
        """Actualiza una configuración"""
        return await self.configuration_service.update_configuration(
            key, new_value, user_id, reason
        )
    
    async def get_configuration_history(self, key: str) -> List[ConfigurationHistory]:
        """Obtiene el histórico de una configuración"""
        return await self.configuration_service.get_configuration_history(key)
    
    async def validate_configuration_change(
        self, 
        key: str, 
        new_value: str
    ) -> List[str]:
        """Valida un cambio de configuración antes de aplicarlo"""
        config = await self.configuration_service.config_repository.get_by_key(key)
        if not config:
            return ["Configuración no encontrada"]
        
        return self.configuration_service.validate_configuration_value(config, new_value)
    
    async def initialize_default_configurations(self) -> List[Configuration]:
        """Inicializa las configuraciones por defecto del sistema"""
        default_configs = [
            Configuration(
                key="porc_aditivo",
                name="Porcentaje de Aditivo",
                description="Porcentaje de aditivo sobre el peso de la cera",
                value="8.0",
                type="percentage",
                category="porcentajes",
                min_value=0,
                max_value=20
            ),
            Configuration(
                key="porc_fragancia",
                name="Porcentaje de Fragancia",
                description="Porcentaje de fragancia sobre el peso de la cera",
                value="6.0",
                type="percentage",
                category="porcentajes",
                min_value=0,
                max_value=15
            ),
            Configuration(
                key="porc_ganancia",
                name="Porcentaje de Ganancia",
                description="Porcentaje de ganancia sobre el costo base",
                value="250.0",
                type="percentage",
                category="porcentajes",
                min_value=1,
                max_value=500
            ),
            Configuration(
                key="porc_detalle",
                name="Porcentaje de Detalle",
                description="Porcentaje adicional por detalle/complejidad",
                value="20.0",
                type="percentage",
                category="porcentajes",
                min_value=0,
                max_value=100
            ),
            Configuration(
                key="porc_admin",
                name="Gastos Administrativos",
                description="Porcentaje de gastos administrativos",
                value="10.0",
                type="percentage",
                category="porcentajes",
                min_value=0,
                max_value=30
            ),
            Configuration(
                key="valor_cera_kg",
                name="Precio Cera por Kg",
                description="Precio de la cera por kilogramo",
                value="15000",
                type="price",
                category="precios_insumos",
                min_value=1000
            ),
            Configuration(
                key="valor_aditivo_kg",
                name="Precio Aditivo por Kg",
                description="Precio del aditivo por kilogramo",
                value="8000",
                type="price",
                category="precios_insumos",
                min_value=1000
            ),
            Configuration(
                key="multiplo_redondeo",
                name="Múltiplo de Redondeo",
                description="Múltiplo para redondeo de precios finales",
                value="500",
                type="multiplier",
                category="redondeo",
                min_value=1
            )
        ]
        
        created_configs = []
        for config in default_configs:
            existing = await self.configuration_service.config_repository.get_by_key(config.key)
            if not existing:
                created = await self.configuration_service.config_repository.create(config)
                created_configs.append(created)
        
        return created_configs
