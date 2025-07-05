#!/bin/bash
# 🎯 Implementación Completa de Reglas de Negocio - Sistema Vel Arte
# Implementa motor de cálculos parametrizable para costos de velas

echo "🎯 IMPLEMENTANDO REGLAS DE NEGOCIO COMPLETAS"
echo "=========================================="
echo "⏰ Iniciado: $(date)"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# FASE 1: CREAR ENTIDADES DE DOMINIO PARA REGLAS DE NEGOCIO
create_business_entities() {
    echo ""
    echo "🏗️ FASE 1: CREANDO ENTIDADES DE DOMINIO"
    echo "======================================="
    
    log_info "Creando estructura para reglas de negocio..."
    
    # Crear estructura Clean Architecture para business rules
    mkdir -p business-rules-service/src/{domain/{entities,repositories,services},use_cases,infrastructure/{database,external_services},api/{routes,middleware,schemas},config}
    mkdir -p business-rules-service/src/domain/value_objects
    
    # Crear Dockerfile para business-rules-service
    cat > business-rules-service/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8003

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
EOF

    # Requirements para business rules service
    cat > business-rules-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pymongo==4.6.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
email-validator==2.0.0
python-decimal==0.10.0
EOF

    # Entidad Configuration (para parámetros dinámicos)
    cat > business-rules-service/src/domain/entities/configuration.py << 'EOF'
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
EOF

    # Entidad Molde mejorada
    cat > business-rules-service/src/domain/entities/molde.py << 'EOF'
from pydantic import BaseModel, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class Molde(BaseModel):
    """Entidad Molde con datos técnicos para cálculos"""
    id: Optional[str] = None
    nombre: str
    codigo: str  # Código único
    peso_figura: Decimal  # Peso final en gramos
    longitud_pabilo: Decimal  # Longitud en metros
    complejidad: str  # "simple", "intermedio", "complejo"
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('peso_figura', 'longitud_pabilo')
    def validate_positive_values(cls, v):
        if v <= 0:
            raise ValueError("Los valores deben ser mayores a cero")
        return v
    
    @validator('complejidad')
    def validate_complejidad(cls, v):
        valid_values = ["simple", "intermedio", "complejo"]
        if v.lower() not in valid_values:
            raise ValueError(f"Complejidad debe ser uno de: {valid_values}")
        return v.lower()

class MoldeInsumo(BaseModel):
    """Relación entre molde e insumos específicos"""
    id: Optional[str] = None
    molde_id: str
    insumo_id: str
    cantidad_base: Decimal  # Cantidad base requerida
    unidad: str  # "gramos", "ml", "gotas", "metros"
    es_opcional: bool = False
EOF

    # Entidad Producto (catálogo)
    cat > business-rules-service/src/domain/entities/producto.py << 'EOF'
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
EOF

    # Value Objects para cálculos
    cat > business-rules-service/src/domain/value_objects/calculation_params.py << 'EOF'
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
EOF

    log_success "Entidades de dominio creadas"
}

# FASE 2: CREAR SERVICIOS DE DOMINIO
create_domain_services() {
    echo ""
    echo "🧮 FASE 2: CREANDO SERVICIOS DE DOMINIO"
    echo "======================================="
    
    log_info "Implementando motor de cálculos..."
    
    # Servicio de cálculo de costos
    cat > business-rules-service/src/domain/services/cost_calculation_service.py << 'EOF'
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
EOF

    # Servicio de configuración
    cat > business-rules-service/src/domain/services/configuration_service.py << 'EOF'
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
EOF

    log_success "Servicios de dominio creados"
}

# FASE 3: CREAR CASOS DE USO
create_use_cases() {
    echo ""
    echo "🎪 FASE 3: CREANDO CASOS DE USO"
    echo "==============================="
    
    log_info "Implementando casos de uso para cálculos..."
    
    # Caso de uso: Calcular precio de producto
    cat > business-rules-service/src/use_cases/calculate_product_price.py << 'EOF'
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
EOF

    # Caso de uso: Gestionar configuraciones
    cat > business-rules-service/src/use_cases/manage_configurations.py << 'EOF'
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
EOF

    log_success "Casos de uso creados"
}

# FASE 4: ACTUALIZAR DOCKER COMPOSE
update_docker_compose() {
    echo ""
    echo "🐳 FASE 4: ACTUALIZANDO DOCKER COMPOSE"
    echo "======================================"
    
    log_info "Agregando business-rules-service al docker-compose..."
    
    # Backup del docker-compose actual
    cp docker-compose.yml docker-compose.yml.backup
    
    # Crear nuevo docker-compose con business rules service
    cat > docker-compose.yml << 'EOF'
services:
  mongodb:
    image: mongo:7.0
    container_name: vel_arte_mongodb
    ports:
      - "27018:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: vel_arte_db
    volumes:
      - mongodb_data:/data/db
    networks:
      - vel_arte_network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 30s
      timeout: 10s
      retries: 3

  auth-service:
    build: ./auth-service
    container_name: vel_arte_auth
    ports:
      - "8001:8000"
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongodb:27017/vel_arte_db?authSource=admin
    networks:
      - vel_arte_network
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  product-service:
    build: ./product-service
    container_name: vel_arte_products
    ports:
      - "8002:8001"
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongodb:27017/vel_arte_db?authSource=admin
    networks:
      - vel_arte_network
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  business-rules-service:
    build: ./business-rules-service
    container_name: vel_arte_business_rules
    ports:
      - "8003:8003"
    environment:
      - MONGODB_URL=mongodb://admin:password123@mongodb:27017/vel_arte_db?authSource=admin
    networks:
      - vel_arte_network
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  api-gateway:
    build: ./api-gateway
    container_name: vel_arte_gateway
    ports:
      - "8000:8000"
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8000
      - PRODUCT_SERVICE_URL=http://product-service:8001
      - BUSINESS_RULES_SERVICE_URL=http://business-rules-service:8003
    networks:
      - vel_arte_network
    depends_on:
      auth-service:
        condition: service_healthy
      product-service:
        condition: service_healthy
      business-rules-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mongodb_data:

networks:
  vel_arte_network:
    driver: bridge
EOF

    log_success "Docker Compose actualizado"
}

# Función principal
main() {
    log_info "Iniciando implementación de reglas de negocio completas..."
    
    create_business_entities
    create_domain_services
    create_use_cases
    update_docker_compose
    
    echo ""
    echo "🎉 REGLAS DE NEGOCIO IMPLEMENTADAS"
    echo "================================="
    log_success "Sistema completo implementado:"
    echo "  ✅ Entidades de dominio (Configuration, Molde, Producto)"
    echo "  ✅ Motor de cálculos parametrizable"
    echo "  ✅ Servicios de dominio (CostCalculation, Configuration)"
    echo "  ✅ Casos de uso (CalculatePrice, ManageConfigurations)"
    echo "  ✅ Microservicio business-rules-service"
    echo "  ✅ Docker Compose actualizado"
    echo ""
    log_info "Próximos pasos:"
    echo "  1. Completar implementación (repositorios, APIs, frontend)"
    echo "  2. Reconstruir y probar servicios"
    echo "  3. Cargar configuraciones por defecto"
    echo "  4. Preparar para GitHub"
    echo ""
    log_warning "Para continuar ejecuta:"
    echo "  ./complete_business_rules_implementation.sh"
}

# Ejecutar función principal
main "$@"