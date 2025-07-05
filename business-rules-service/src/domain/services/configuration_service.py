from typing import Dict, List, Optional
from decimal import Decimal
from ..entities.configuration import Configuration, ConfigurationHistory
from ..value_objects.calculation_params import CalculationParams

class ConfigurationService:
    """Servicio para manejo de configuraciones dinámicas"""
    
    def __init__(self, config_repository):
        self.config_repository = config_repository
    
    async def get_calculation_params(self) -> CalculationParams:
        """Obtiene todos los parámetros activos para cálculos"""
        configs = await self.config_repository.get_active_configs()
        
        # Valores por defecto en caso de que no existan configuraciones
        defaults = {
            'porc_aditivo': Decimal('8.0'),
            'porc_fragancia': Decimal('6.0'),
            'porc_ganancia': Decimal('250.0'),
            'porc_detalle': Decimal('20.0'),
            'porc_admin': Decimal('10.0'),
            'valor_cera_kg': Decimal('15000'),
            'valor_aditivo_kg': Decimal('8000'),
            'valor_fragancia_ml': Decimal('150'),
            'valor_colorante_gota': Decimal('50'),
            'valor_pabilo_metro': Decimal('200'),
            'multiplo_redondeo': 500,
        }
        
        # Sobrescribir con valores de la base de datos
        params_dict = defaults.copy()
        for config in configs:
            if config.key in params_dict:
                if config.key == 'multiplo_redondeo':
                    params_dict[config.key] = int(config.value)
                else:
                    params_dict[config.key] = Decimal(config.value)
        
        # Obtener descuentos por cantidad
        descuentos = await self.config_repository.get_quantity_discounts()
        
        return CalculationParams(
            **params_dict,
            descuentos_cantidad=descuentos
        )
    
    async def update_configuration(
        self, 
        key: str, 
        new_value: str, 
        user_id: str,
        reason: Optional[str] = None
    ) -> Configuration:
        """Actualiza una configuración y registra el histórico"""
        
        # Obtener configuración actual
        current_config = await self.config_repository.get_by_key(key)
        if not current_config:
            raise ValueError(f"Configuración con key '{key}' no encontrada")
        
        # Guardar en histórico
        history = ConfigurationHistory(
            configuration_id=current_config.id,
            old_value=current_config.value,
            new_value=new_value,
            changed_by=user_id,
            changed_at=datetime.utcnow(),
            reason=reason
        )
        
        await self.config_repository.save_history(history)
        
        # Actualizar configuración
        current_config.value = new_value
        current_config.updated_at = datetime.utcnow()
        
        return await self.config_repository.update(current_config)
    
    async def get_configuration_history(self, key: str) -> List[ConfigurationHistory]:
        """Obtiene el histórico de cambios de una configuración"""
        config = await self.config_repository.get_by_key(key)
        if not config:
            return []
        
        return await self.config_repository.get_history(config.id)
    
    def validate_configuration_value(self, config: Configuration, new_value: str) -> List[str]:
        """Valida que un nuevo valor sea válido para una configuración"""
        errors = []
        
        try:
            if config.type == "percentage":
                val = Decimal(new_value)
                if val < 0 or val > 100:
                    errors.append("Porcentaje debe estar entre 0 y 100")
            elif config.type == "price":
                val = Decimal(new_value)
                if val < 0:
                    errors.append("Precio no puede ser negativo")
            elif config.type == "multiplier":
                val = Decimal(new_value)
                if val <= 0:
                    errors.append("Multiplicador debe ser mayor a 0")
            
            # Validar rangos específicos si están definidos
            if config.min_value is not None:
                val = Decimal(new_value)
                if val < config.min_value:
                    errors.append(f"Valor debe ser mayor o igual a {config.min_value}")
            
            if config.max_value is not None:
                val = Decimal(new_value)
                if val > config.max_value:
                    errors.append(f"Valor debe ser menor o igual a {config.max_value}")
                    
        except (ValueError, TypeError):
            errors.append("Formato de valor inválido")
        
        return errors
