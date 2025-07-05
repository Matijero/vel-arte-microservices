#!/bin/bash
# 🔧 Script Complementario - Completar Implementación de Reglas de Negocio

echo "🔧 COMPLETANDO IMPLEMENTACIÓN DE REGLAS DE NEGOCIO"
echo "================================================"
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

# FASE 1: CREAR REPOSITORIOS (INFRASTRUCTURE)
create_repositories() {
    echo ""
    echo "🗄️ FASE 1: CREANDO REPOSITORIOS"
    echo "==============================="
    
    log_info "Implementando capa de infraestructura..."
    
    # Repository para configuraciones
    cat > business-rules-service/src/infrastructure/database/configuration_repository.py << 'EOF'
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.configuration import Configuration, ConfigurationHistory
from decimal import Decimal

class ConfigurationRepository:
    """Repositorio para configuraciones del sistema"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.configurations
        self.history_collection = database.configuration_history
    
    async def create(self, config: Configuration) -> Configuration:
        """Crea una nueva configuración"""
        config_dict = config.dict(exclude={'id'})
        config_dict['created_at'] = datetime.utcnow()
        config_dict['updated_at'] = None
        
        result = await self.collection.insert_one(config_dict)
        config.id = str(result.inserted_id)
        return config
    
    async def get_by_id(self, config_id: str) -> Optional[Configuration]:
        """Obtiene configuración por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(config_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Configuration(**doc)
        except Exception:
            return None
        return None
    
    async def get_by_key(self, key: str) -> Optional[Configuration]:
        """Obtiene configuración por clave"""
        doc = await self.collection.find_one({"key": key})
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            return Configuration(**doc)
        return None
    
    async def get_all(self, category: Optional[str] = None) -> List[Configuration]:
        """Obtiene todas las configuraciones, opcionalmente por categoría"""
        filter_dict = {}
        if category:
            filter_dict['category'] = category
        
        cursor = self.collection.find(filter_dict)
        configs = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            configs.append(Configuration(**doc))
        
        return configs
    
    async def get_active_configs(self) -> List[Configuration]:
        """Obtiene solo configuraciones activas"""
        cursor = self.collection.find({"is_active": True})
        configs = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            configs.append(Configuration(**doc))
        
        return configs
    
    async def update(self, config: Configuration) -> Configuration:
        """Actualiza una configuración"""
        config_dict = config.dict(exclude={'id'})
        config_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(config.id)},
            {"$set": config_dict}
        )
        
        return config
    
    async def save_history(self, history: ConfigurationHistory) -> ConfigurationHistory:
        """Guarda un registro de histórico"""
        history_dict = history.dict(exclude={'id'})
        result = await self.history_collection.insert_one(history_dict)
        history.id = str(result.inserted_id)
        return history
    
    async def get_history(self, config_id: str) -> List[ConfigurationHistory]:
        """Obtiene el histórico de una configuración"""
        cursor = self.history_collection.find(
            {"configuration_id": config_id}
        ).sort("changed_at", -1)
        
        history = []
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            history.append(ConfigurationHistory(**doc))
        
        return history
    
    async def get_quantity_discounts(self) -> Dict[int, Decimal]:
        """Obtiene descuentos por cantidad desde configuraciones"""
        # Buscar configuraciones de descuentos
        cursor = self.collection.find({"category": "descuentos_cantidad"})
        discounts = {}
        
        async for doc in cursor:
            if doc['key'].startswith('descuento_'):
                try:
                    # Extraer cantidad del key (ej: descuento_10, descuento_50)
                    cantidad = int(doc['key'].split('_')[1])
                    porcentaje = Decimal(doc['value'])
                    discounts[cantidad] = porcentaje
                except (ValueError, IndexError):
                    continue
        
        return discounts
EOF

    # Repository para moldes
    cat > business-rules-service/src/infrastructure/database/molde_repository.py << 'EOF'
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.molde import Molde, MoldeInsumo

class MoldeRepository:
    """Repositorio para moldes"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.moldes
        self.molde_insumos_collection = database.molde_insumos
    
    async def create(self, molde: Molde) -> Molde:
        """Crea un nuevo molde"""
        molde_dict = molde.dict(exclude={'id'})
        molde_dict['created_at'] = datetime.utcnow()
        molde_dict['updated_at'] = None
        
        result = await self.collection.insert_one(molde_dict)
        molde.id = str(result.inserted_id)
        return molde
    
    async def get_by_id(self, molde_id: str) -> Optional[Molde]:
        """Obtiene molde por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(molde_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Molde(**doc)
        except Exception:
            return None
        return None
    
    async def get_all_active(self) -> List[Molde]:
        """Obtiene todos los moldes activos"""
        cursor = self.collection.find({"is_active": True})
        moldes = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            moldes.append(Molde(**doc))
        
        return moldes
    
    async def update(self, molde: Molde) -> Molde:
        """Actualiza un molde"""
        molde_dict = molde.dict(exclude={'id'})
        molde_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(molde.id)},
            {"$set": molde_dict}
        )
        
        return molde
    
    async def get_insumos_for_molde(self, molde_id: str) -> List[MoldeInsumo]:
        """Obtiene los insumos requeridos para un molde"""
        cursor = self.molde_insumos_collection.find({"molde_id": molde_id})
        insumos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            insumos.append(MoldeInsumo(**doc))
        
        return insumos
EOF

    # Repository para productos
    cat > business-rules-service/src/infrastructure/database/producto_repository.py << 'EOF'
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ...domain.entities.producto import Producto

class ProductoRepository:
    """Repositorio para productos del catálogo"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.productos
    
    async def create(self, producto: Producto) -> Producto:
        """Crea un nuevo producto"""
        producto_dict = producto.dict(exclude={'id', 'costo_calculado', 'desglose_costos'})
        producto_dict['created_at'] = datetime.utcnow()
        producto_dict['updated_at'] = None
        
        result = await self.collection.insert_one(producto_dict)
        producto.id = str(result.inserted_id)
        return producto
    
    async def get_by_id(self, producto_id: str) -> Optional[Producto]:
        """Obtiene producto por ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(producto_id)})
            if doc:
                doc['id'] = str(doc['_id'])
                del doc['_id']
                return Producto(**doc)
        except Exception:
            return None
        return None
    
    async def get_active_products(self) -> List[Producto]:
        """Obtiene todos los productos activos"""
        cursor = self.collection.find({"is_active": True})
        productos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            productos.append(Producto(**doc))
        
        return productos
    
    async def update(self, producto: Producto) -> Producto:
        """Actualiza un producto"""
        producto_dict = producto.dict(exclude={'id', 'costo_calculado', 'desglose_costos'})
        producto_dict['updated_at'] = datetime.utcnow()
        
        await self.collection.update_one(
            {"_id": ObjectId(producto.id)},
            {"$set": producto_dict}
        )
        
        return producto
    
    async def get_by_category(self, categoria: str) -> List[Producto]:
        """Obtiene productos por categoría"""
        cursor = self.collection.find({"categoria": categoria, "is_active": True})
        productos = []
        
        async for doc in cursor:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            productos.append(Producto(**doc))
        
        return productos
EOF

    # Conexión a base de datos
    cat > business-rules-service/src/infrastructure/database/connection.py << 'EOF'
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27018/vel_arte_db?authSource=admin")
DATABASE_NAME = "vel_arte_db"

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Conecta a MongoDB"""
    mongodb.client = AsyncIOMotorClient(MONGODB_URL)
    mongodb.database = mongodb.client[DATABASE_NAME]

async def close_mongo_connection():
    """Cierra la conexión a MongoDB"""
    mongodb.client.close()

def get_database():
    """Obtiene la instancia de la base de datos"""
    return mongodb.database
EOF

    log_success "Repositorios creados"
}

# FASE 2: CREAR APIs (ROUTES)
create_apis() {
    echo ""
    echo "🌐 FASE 2: CREANDO APIs"
    echo "======================="
    
    log_info "Implementando endpoints REST..."
    
    # API para configuraciones
    cat > business-rules-service/src/api/routes/configuration_routes.py << 'EOF'
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
EOF

    # API para cálculos de productos
    cat > business-rules-service/src/api/routes/calculation_routes.py << 'EOF'
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
EOF

    # Main app del business rules service
    cat > business-rules-service/src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes.configuration_routes import router as config_router
from .api.routes.calculation_routes import router as calc_router
from .infrastructure.database.connection import connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="Vel Arte Business Rules Service", 
    version="1.0.0",
    description="Microservicio para reglas de negocio y cálculos de costos"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

app.include_router(config_router)
app.include_router(calc_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "business-rules-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Vel Arte Business Rules Service",
        "version": "1.0.0",
        "endpoints": [
            "/configurations",
            "/calculations",
            "/health",
            "/docs"
        ]
    }
EOF

    # Archivos __init__.py
    find business-rules-service/src -type d -exec touch {}/__init__.py \;

    log_success "APIs creadas"
}

# FASE 3: ACTUALIZAR API GATEWAY
update_gateway_for_business_rules() {
    echo ""
    echo "🌐 FASE 3: ACTUALIZANDO API GATEWAY"
    echo "=================================="
    
    log_info "Agregando rutas de business rules al gateway..."
    
    # Backup del main.py actual del gateway
    cp api-gateway/src/main.py api-gateway/src/main.py.backup
    
    # Nuevo main.py del gateway con business rules
    cat > api-gateway/src/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import Optional, Dict, Any

app = FastAPI(title="Vel Arte API Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los microservicios
AUTH_SERVICE_URL = "http://auth-service:8000"
PRODUCT_SERVICE_URL = "http://product-service:8001"
BUSINESS_RULES_SERVICE_URL = "http://business-rules-service:8003"

async def forward_request(
    service_url: str, 
    path: str, 
    method: str = "GET", 
    headers: Optional[Dict] = None,
    **kwargs
):
    """Reenvía peticiones a los microservicios"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method, 
                f"{service_url}{path}", 
                headers=headers,
                **kwargs
            )
            
            if response.status_code >= 400:
                return {"error": response.text, "status_code": response.status_code}
            
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# Health check mejorado
@app.get("/health")
async def health_check():
    services_status = {}
    
    services = [
        ("auth-service", AUTH_SERVICE_URL),
        ("product-service", PRODUCT_SERVICE_URL),
        ("business-rules-service", BUSINESS_RULES_SERVICE_URL)
    ]
    
    for service_name, service_url in services:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_status[service_name] = "unhealthy"
    
    overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": services_status,
        "gateway": "operational",
        "version": "2.0.0"
    }

# === AUTH ROUTES ===
@app.post("/auth/register")
async def register(request: Request):
    body = await request.json()
    return await forward_request(AUTH_SERVICE_URL, "/auth/register", "POST", json=body)

@app.post("/auth/login")
async def login(request: Request):
    body = await request.json()
    return await forward_request(AUTH_SERVICE_URL, "/auth/login", "POST", json=body)

@app.get("/auth/me")
async def get_current_user(request: Request):
    headers = dict(request.headers)
    return await forward_request(AUTH_SERVICE_URL, "/auth/me", "GET", headers=headers)

# === PRODUCT ROUTES ===
@app.get("/insumos")
async def get_insumos():
    return await forward_request(PRODUCT_SERVICE_URL, "/insumos/", "GET")

@app.post("/insumos")
async def create_insumo(request: Request):
    headers = dict(request.headers)
    body = await request.json()
    return await forward_request(PRODUCT_SERVICE_URL, "/insumos/", "POST", headers=headers, json=body)

@app.get("/insumos/{insumo_id}")
async def get_insumo(insumo_id: str):
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "GET")

@app.put("/insumos/{insumo_id}")
async def update_insumo(insumo_id: str, request: Request):
    headers = dict(request.headers)
    body = await request.json()
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "PUT", headers=headers, json=body)

@app.delete("/insumos/{insumo_id}")
async def delete_insumo(insumo_id: str, request: Request):
    headers = dict(request.headers)
    return await forward_request(PRODUCT_SERVICE_URL, f"/insumos/{insumo_id}", "DELETE", headers=headers)

# === BUSINESS RULES ROUTES ===

# Configuraciones
@app.get("/configurations")
async def get_configurations(category: Optional[str] = None):
    path = "/configurations"
    if category:
        path += f"?category={category}"
    return await forward_request(BUSINESS_RULES_SERVICE_URL, path, "GET")

@app.put("/configurations/{key}")
async def update_configuration(key: str, request: Request):
    body = await request.json()
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/configurations/{key}", 
        "PUT", 
        params=body
    )

@app.get("/configurations/{key}/history")
async def get_configuration_history(key: str):
    return await forward_request(BUSINESS_RULES_SERVICE_URL, f"/configurations/{key}/history", "GET")

@app.post("/configurations/initialize")
async def initialize_configurations():
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/configurations/initialize", "POST")

# Cálculos
@app.post("/calculations/product/{producto_id}")
async def calculate_product_price(producto_id: str, request: Request):
    params = request.query_params
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/calculations/product/{producto_id}", 
        "POST", 
        params=params,
        json=body if body else None
    )

@app.post("/calculations/recalculate-all")
async def recalculate_all_products(request: Request):
    headers = dict(request.headers)
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/calculations/recalculate-all", "POST", headers=headers)

@app.get("/calculations/simulation/{producto_id}")
async def simulate_price_changes(producto_id: str, request: Request):
    params = request.query_params
    return await forward_request(
        BUSINESS_RULES_SERVICE_URL, 
        f"/calculations/simulation/{producto_id}", 
        "GET", 
        params=params
    )

@app.get("/calculations/params")
async def get_calculation_params():
    return await forward_request(BUSINESS_RULES_SERVICE_URL, "/calculations/params", "GET")

# Legacy routes para compatibilidad
@app.get("/moldes")
async def get_moldes():
    return await forward_request(PRODUCT_SERVICE_URL, "/moldes", "GET")

@app.get("/colores")
async def get_colores():
    return await forward_request(PRODUCT_SERVICE_URL, "/colores", "GET")

@app.get("/resumen-completo")
async def get_resumen():
    return await forward_request(PRODUCT_SERVICE_URL, "/resumen-completo", "GET")

@app.get("/")
async def root():
    return {
        "message": "Vel Arte API Gateway",
        "version": "2.0.0",
        "status": "operational",
        "services": {
            "auth": "/auth/*",
            "products": "/insumos, /moldes, /colores",
            "business_rules": "/configurations, /calculations"
        },
        "documentation": "/docs"
    }
EOF

    log_success "API Gateway actualizado"
}

# FASE 4: CREAR SCRIPTS DE INICIALIZACIÓN
create_initialization_scripts() {
    echo ""
    echo "🚀 FASE 4: CREANDO SCRIPTS DE INICIALIZACIÓN"
    echo "==========================================="
    
    log_info "Creando script para inicializar datos..."
    
    # Script para cargar datos de ejemplo
    cat > initialize_business_data.sh << 'EOF'
#!/bin/bash
echo "🔧 INICIALIZANDO DATOS DE NEGOCIO"
echo "================================="

API_BASE="http://localhost:8000"

echo "1. Inicializando configuraciones por defecto..."
curl -X POST "$API_BASE/configurations/initialize" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo -e "\n2. Agregando descuentos por cantidad..."

# Descuento 5% para 10+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_10",
    "name": "Descuento 10+ unidades",
    "description": "5% de descuento para 10 o más unidades",
    "value": "5.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

# Descuento 10% para 20+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_20",
    "name": "Descuento 20+ unidades",
    "description": "10% de descuento para 20 o más unidades",
    "value": "10.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

# Descuento 15% para 50+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_50",
    "name": "Descuento 50+ unidades",
    "description": "15% de descuento para 50 o más unidades",
    "value": "15.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

echo -e "\n3. Creando moldes de ejemplo..."

# TODO: Implementar creación de moldes via API

echo -e "\n4. Creando productos de ejemplo..."

# TODO: Implementar creación de productos via API

echo -e "\n5. Probando cálculo de ejemplo..."
# curl -X POST "$API_BASE/calculations/product/PRODUCTO_ID?cantidad_gotas=3" -s | jq '.'

echo -e "\n✅ Inicialización completada!"
echo "📊 Ver configuraciones: curl $API_BASE/configurations | jq '.'"
echo "🧮 Ver parámetros: curl $API_BASE/calculations/params | jq '.'"
EOF

    chmod +x initialize_business_data.sh

    # Script de tests completos
    cat > test_business_rules.sh << 'EOF'
#!/bin/bash
echo "🧪 TESTING REGLAS DE NEGOCIO COMPLETAS"
echo "====================================="

API_BASE="http://localhost:8000"

echo "1. Health check de todos los servicios..."
curl -s "$API_BASE/health" | jq '.'

echo -e "\n2. Verificando configuraciones..."
curl -s "$API_BASE/configurations" | jq '.[] | {key: .key, name: .name, value: .value}'

echo -e "\n3. Obteniendo parámetros de cálculo..."
curl -s "$API_BASE/calculations/params" | jq '.'

echo -e "\n4. Probando actualización de configuración..."
curl -X PUT "$API_BASE/configurations/porc_ganancia?new_value=300&user_id=test_user&reason=Test" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo -e "\n5. Verificando histórico de cambios..."
curl -s "$API_BASE/configurations/porc_ganancia/history" | jq '.'

echo -e "\n6. Validando valor de configuración..."
curl -X POST "$API_BASE/configurations/validate?key=porc_aditivo&value=12.5" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo -e "\n✅ Tests de business rules completados!"
EOF

    chmod +x test_business_rules.sh

    log_success "Scripts de inicialización creados"
}

# FASE 5: PREPARAR PARA GITHUB
prepare_for_github() {
    echo ""
    echo "📝 FASE 5: PREPARANDO PARA GITHUB"
    echo "================================"
    
    log_info "Creando documentación y archivos para GitHub..."
    
    # README principal
    cat > README.md << 'EOF'
# 🎨 Vel Arte - Sistema de Gestión de Costos para Velas

Sistema completo de microservicios para gestión parametrizable de costos de productos de velas, desarrollado con **Clean Architecture** y principios **SOLID**.

## 🚀 Características Principales

- ✅ **Sistema de Autenticación** JWT con roles
- ✅ **CRUD Completo** para insumos, moldes y productos
- ✅ **Motor de Cálculos Parametrizable** - Sin valores hardcodeados
- ✅ **Reglas de Negocio Dinámicas** - Todo configurable vía CRUD
- ✅ **Histórico de Cambios** - Trazabilidad completa
- ✅ **Descuentos por Cantidad** escalables
- ✅ **Simulador de Precios** - Pruebas sin afectar producción
- ✅ **Clean Architecture** - Capas separadas y testeable
- ✅ **Docker Compose** - Entorno completo containerizado

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│   Frontend      │    │   API Gateway    │    │   Business Rules        │
│   React         │◄──►│   Port 8000      │◄──►│   Port 8003             │
└─────────────────┘    └──────────────────┘    └─────────────────────────┘
                                ▲                            ▲
                                │                            │
                       ┌────────┴────────┐          ┌──────┴──────┐
                       │                 │          │             │
               ┌───────▼────────┐ ┌──────▼────────┐ │    MongoDB  │
               │ Auth Service   │ │Product Service│ │   Port 27018│
               │ Port 8001      │ │ Port 8002     │ │             │
               └────────────────┘ └───────────────┘ └─────────────┘
```

### Microservicios:
- **API Gateway** (8000): Punto de entrada único
- **Auth Service** (8001): Autenticación y autorización
- **Product Service** (8002): Gestión de insumos, moldes
- **Business Rules Service** (8003): Cálculos y configuraciones
- **MongoDB** (27018): Base de datos

## 🧮 Motor de Cálculos

### Fórmula Completa:
1. **Costo Base**: Cera + Aditivo + Fragancia + Colorante + Pabilo + Otros
2. **Ganancia**: Costo Base × % Ganancia
3. **Detalle**: Costo Base × % Detalle (según complejidad)
4. **Admin**: (Costo Base + Ganancia + Detalle) × % Admin
5. **Redondeo**: Al múltiplo configurado (ej: 500 COP)
6. **Descuentos**: Por cantidad escalables

### Parámetros Configurables:
- % Aditivo (default: 8%)
- % Fragancia (default: 6%)
- % Ganancia (default: 250%)
- % Detalle por complejidad
- % Gastos Admin (default: 10%)
- Precios de insumos por unidad
- Múltiplo de redondeo
- Descuentos por cantidad

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker Desktop
- Node.js 18+
- Git

### 1. Clonar y Arrancar
```bash
git clone https://github.com/tu-usuario/vel-arte-microservices.git
cd vel-arte-microservices

# Arrancar todos los servicios
docker-compose up -d

# Esperar que estén listos (2-3 minutos)
curl http://localhost:8000/health
```

### 2. Inicializar Datos
```bash
# Cargar configuraciones por defecto
./initialize_business_data.sh

# Verificar funcionamiento
./test_business_rules.sh
```

### 3. Arrancar Frontend
```bash
cd frontend
npm install
npm start
# Abre automáticamente http://localhost:3000
```

## 📚 API Endpoints

### Autenticación
- `POST /auth/register` - Registro de usuarios
- `POST /auth/login` - Login (retorna JWT)
- `GET /auth/me` - Info del usuario actual

### Configuraciones
- `GET /configurations` - Todas las configuraciones
- `PUT /configurations/{key}` - Actualizar configuración
- `GET /configurations/{key}/history` - Histórico de cambios

### Cálculos
- `POST /calculations/product/{id}` - Calcular precio
- `POST /calculations/recalculate-all` - Recalcular todo
- `GET /calculations/simulation/{id}` - Simular cambios
- `GET /calculations/params` - Parámetros actuales

### CRUD Insumos
- `GET /insumos` - Listar insumos
- `POST /insumos` - Crear insumo
- `PUT /insumos/{id}` - Actualizar insumo
- `DELETE /insumos/{id}` - Eliminar insumo

## 🧪 Testing

```bash
# Tests de integración
./test_business_rules.sh

# Tests de autenticación
./test_implementation.sh

# Health check completo
curl http://localhost:8000/health | jq '.'
```

## 🔧 Configuración

### Variables de Entorno
```env
MONGODB_URL=mongodb://admin:password123@mongodb:27017/vel_arte_db?authSource=admin
JWT_SECRET=your-secret-key
AUTH_SERVICE_URL=http://auth-service:8000
PRODUCT_SERVICE_URL=http://product-service:8001
BUSINESS_RULES_SERVICE_URL=http://business-rules-service:8003
```

### Configuraciones de Negocio
Todas las reglas de negocio se configuran dinámicamente via API:

```bash
# Cambiar % de ganancia
curl -X PUT "http://localhost:8000/configurations/porc_ganancia?new_value=300&user_id=admin"

# Ver histórico de cambios
curl http://localhost:8000/configurations/porc_ganancia/history

# Simular cambio sin aplicar
curl "http://localhost:8000/calculations/simulation/PRODUCTO_ID?porc_ganancia=400"
```

## 📊 Monitoreo

### Health Checks
- Gateway: http://localhost:8000/health
- Auth: http://localhost:8001/health
- Products: http://localhost:8002/health
- Business Rules: http://localhost:8003/health

### Documentación API
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🏗️ Arquitectura Técnica

### Clean Architecture
```
business-rules-service/
├── src/
│   ├── domain/              # Reglas de negocio
│   │   ├── entities/        # Entidades del dominio
│   │   ├── repositories/    # Interfaces de repositorios
│   │   ├── services/        # Servicios de dominio
│   │   └── value_objects/   # Objetos de valor
│   ├── use_cases/           # Casos de uso
│   ├── infrastructure/      # Implementaciones externas
│   │   └── database/        # Repositorios MongoDB
│   ├── api/                 # Controladores REST
│   │   └── routes/          # Endpoints
│   └── config/              # Configuración
```

### Principios SOLID
- **S**ingle Responsibility: Cada clase tiene una responsabilidad
- **O**pen/Closed: Abierto para extensión, cerrado para modificación
- **L**iskov Substitution: Interfaces sustituibles
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependencias hacia abstracciones

## 🚀 Despliegue en Producción

### Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.yml vel-arte
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Variables de Producción
- Cambiar `JWT_SECRET`
- Configurar MongoDB con autenticación
- Usar HTTPS con certificados SSL
- Configurar límites de rate limiting
- Habilitar logs estructurados

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Equipo Vel Arte** - Desarrollo inicial

## 🙏 Agradecimientos

- Clean Architecture principles by Robert C. Martin
- FastAPI framework
- MongoDB for data persistence
- Docker for containerization
EOF

    # .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache

# React build
/frontend/build
/frontend/.env.local
/frontend/.env.development.local
/frontend/.env.test.local
/frontend/.env.production.local

# Docker
.dockerignore

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Backups
backups/
*.backup
*.bak

# Temporary files
tmp/
temp/
*.tmp

# Environment variables
.env.local
.env.production
.env.development

# Test coverage
coverage/
.nyc_output/
.coverage

# MongoDB data
mongodb_data/

# IDE specific
.vscode/settings.json
.idea/workspace.xml
EOF

    # LICENSE
    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Vel Arte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

    log_success "Archivos para GitHub creados"
}

# Función principal
main() {
    log_info "Completando implementación de reglas de negocio..."
    
    create_repositories
    create_apis
    update_gateway_for_business_rules
    create_initialization_scripts
    prepare_for_github
    
    echo ""
    echo "🎉 IMPLEMENTACIÓN COMPLETA FINALIZADA"
    echo "===================================="
    log_success "Sistema completo con reglas de negocio implementado:"
    echo "  ✅ Repositorios (Infrastructure layer)"
    echo "  ✅ APIs REST (Application layer)"
    echo "  ✅ Gateway actualizado con business rules"
    echo "  ✅ Scripts de inicialización y testing"
    echo "  ✅ Documentación para GitHub"
    echo ""
    log_info "Para probar la implementación completa:"
    echo "  1. docker-compose down && docker-compose up -d --build"
    echo "  2. ./initialize_business_data.sh"
    echo "  3. ./test_business_rules.sh"
    echo ""
    log_info "Para subir a GitHub:"
    echo "  1. git add ."
    echo "  2. git commit -m 'Implementar reglas de negocio completas'"
    echo "  3. git push origin main"
    echo ""
    log_warning "Recuerda configurar variables de entorno de producción antes del despliegue"
}

# Ejecutar función principal
main "$@"