from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
import uvicorn
import logging
from contextlib import asynccontextmanager

# Importar nuestras clases de base de datos
from database_manager import (
    db_manager, 
    InsumoRepository, 
    MoldeRepository, 
    ColorRepository
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
from enum import Enum

class TipoInsumo(str, Enum):
    CERA = "cera"
    FRAGANCIA = "fragancia" 
    COLORANTE = "colorante"
    PABILO = "pabilo"
    ADITIVO = "aditivo"
    ENVASE = "envase"
    OTROS = "otros"

class EstadoMolde(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"

# Modelos Pydantic
class InsumoBase(BaseModel):
    codigo: str
    descripcion: str
    tipo: TipoInsumo
    costo_base: float
    cantidad_inventario: int = 0
    unidad_medida: str
    proveedor: Optional[str] = None
    activo: bool = True

class MoldeBase(BaseModel):
    codigo: str
    descripcion: str
    peso_cera_necesario: float
    cantidad_pabilo: int
    estado: EstadoMolde = EstadoMolde.DISPONIBLE
    ubicacion_fisica: Optional[str] = None
    activo: bool = True

class ColorBase(BaseModel):
    codigo: str
    nombre: str
    cantidad_gotas_estandar: int = 10
    activo: bool = True

# Ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    await db_manager.connect()
    logger.info("🚀 Sistema completo con MongoDB y CORS iniciado")
    
    yield
    
    # Shutdown
    await db_manager.close()
    logger.info("🛑 Sistema detenido")

# Aplicación FastAPI
app = FastAPI(
    title="🕯️ Sistema Completo Vel Arte - Con Frontend React",
    version="3.3.0",
    description="""
    ## Sistema completo con Frontend React y Backend FastAPI
    
    ### ✅ Datos Migrados:
    * 📦 **44 Insumos** - Todos tus materiales  
    * 🏺 **140 Moldes** - Toda tu colección de moldes
    * 🎨 **30 Colores** - Paleta completa de colores
    
    ### 🚀 Funcionalidades:
    * Frontend React moderno en puerto 3000
    * Backend FastAPI con CORS habilitado
    * Conexión en tiempo real entre frontend y backend
    
    ### 🌐 URLs:
    * Frontend: http://localhost:3000
    * Backend: http://localhost:8000
    * Docs: http://localhost:8000/docs
    """,
    lifespan=lifespan
)

# ⭐ CONFIGURAR CORS - MUY IMPORTANTE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Por si cambias puerto
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permitir todos los headers
)

# Dependencias
async def get_insumo_repo() -> InsumoRepository:
    return InsumoRepository(db_manager.get_database())

async def get_molde_repo() -> MoldeRepository:
    return MoldeRepository(db_manager.get_database())

async def get_color_repo() -> ColorRepository:
    return ColorRepository(db_manager.get_database())

# =====================================
# ENDPOINTS PRINCIPALES
# =====================================

@app.get("/", tags=["🏠 General"])
async def home():
    return {
        "message": "🎉 Sistema Completo Vel Arte - Frontend + Backend Funcionando",
        "version": "3.3.0",
        "frontend_url": "http://localhost:3000",
        "backend_url": "http://localhost:8000",
        "docs_url": "http://localhost:8000/docs",
        "datos_migrados": {
            "📦 insumos": "44 migrados",
            "🏺 moldes": "140 migrados", 
            "🎨 colores": "30 colores"
        },
        "status": "✅ CORS configurado - Frontend conectado",
        "cors_enabled": True
    }

@app.get("/resumen-completo", tags=["🏠 General"])
async def resumen_completo(
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """Resumen completo de todos los datos para el frontend"""
    
    try:
        # Contar por categorías
        insumos_por_tipo = {}
        insumos = await insumo_repo.listar()
        for insumo in insumos:
            tipo = insumo.get('tipo', 'otros')
            insumos_por_tipo[tipo] = insumos_por_tipo.get(tipo, 0) + 1
        
        moldes_por_estado = {}
        moldes = await molde_repo.listar()
        for molde in moldes:
            estado = molde.get('estado', 'disponible')
            moldes_por_estado[estado] = moldes_por_estado.get(estado, 0) + 1
        
        colores = await color_repo.listar()
        
        return {
            "📊 resumen_general": {
                "total_insumos": len(insumos),
                "total_moldes": len(moldes),
                "total_colores": len(colores)
            },
            "📦 insumos_por_tipo": insumos_por_tipo,
            "🏺 moldes_por_estado": moldes_por_estado,
            "🎨 colores_disponibles": len(colores),
            "💰 valor_aproximado_inventario": sum(
                insumo.get('valor_total', 0) * insumo.get('cantidad_inventario', 0) 
                for insumo in insumos
            ),
            "📈 estadisticas": {
                "molde_mas_caro": max(moldes, key=lambda x: x.get('precio_base_calculado', 0), default={}).get('descripcion', 'N/A'),
                "mayor_stock": max(insumos, key=lambda x: x.get('cantidad_inventario', 0), default={}).get('descripcion', 'N/A')
            },
            "frontend_compatible": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en resumen completo: {e}")
        return {
            "error": str(e),
            "message": "Error obteniendo resumen",
            "📊 resumen_general": {"total_insumos": 0, "total_moldes": 0, "total_colores": 0},
            "📦 insumos_por_tipo": {},
            "🏺 moldes_por_estado": {},
            "🎨 colores_disponibles": 0,
            "💰 valor_aproximado_inventario": 0,
            "📈 estadisticas": {"molde_mas_caro": "Error", "mayor_stock": "Error"}
        }

@app.get("/health", tags=["🏠 General"])
async def health_check():
    """Verificar estado del sistema y base de datos"""
    try:
        await db_manager.client.admin.command('ping')
        
        db = db_manager.get_database()
        stats = {
            "insumos": await db.insumos.count_documents({}),
            "moldes": await db.moldes.count_documents({}),
            "colores": await db.colores.count_documents({})
        }
        
        return {
            "status": "✅ Sistema funcionando perfectamente",
            "database": "✅ MongoDB conectado",
            "frontend": "✅ CORS configurado para React",
            "collections": stats,
            "migracion": "✅ Datos de Excel importados correctamente",
            "urls": {
                "frontend": "http://localhost:3000",
                "backend": "http://localhost:8000",
                "docs": "http://localhost:8000/docs"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "❌ Problema detectado",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# =====================================
# CRUD INSUMOS CON MEJOR FORMATO PARA FRONTEND
# =====================================

@app.get("/insumos", tags=["📦 Insumos"])
async def listar_insumos(
    activos_solo: bool = True,
    tipo: Optional[TipoInsumo] = None,
    stock_bajo: bool = False,
    buscar: Optional[str] = None,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Listar insumos con formato optimizado para frontend"""
    try:
        filtros = {}
        
        if activos_solo:
            filtros["activo"] = True
        
        if tipo:
            filtros["tipo"] = tipo.value
        
        insumos = await repo.listar(filtros)
        
        # Filtro de stock bajo
        if stock_bajo:
            insumos = [i for i in insumos if i.get('cantidad_inventario', 0) <= 10]
        
        # Filtro de búsqueda
        if buscar:
            termino = buscar.lower()
            insumos = [
                i for i in insumos 
                if termino in i.get('descripcion', '').lower() or 
                   termino in i.get('codigo', '').lower()
            ]
        
        return {
            "success": True,
            "total": len(insumos),
            "filtros_aplicados": {
                "activos_solo": activos_solo,
                "tipo": tipo.value if tipo else None,
                "stock_bajo": stock_bajo,
                "buscar": buscar
            },
            "insumos": insumos,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listando insumos: {e}")
        return {
            "success": False,
            "error": str(e),
            "total": 0,
            "insumos": [],
            "message": "Error obteniendo insumos"
        }

@app.get("/moldes", tags=["🏺 Moldes"])
async def listar_moldes(
    estado: Optional[EstadoMolde] = None,
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: MoldeRepository = Depends(get_molde_repo)
):
    """📋 Listar todos los moldes con formato optimizado para frontend"""
    try:
        filtros = {}
        
        if activos_solo:
            filtros["activo"] = True
        
        if estado:
            filtros["estado"] = estado.value
        
        moldes = await repo.listar(filtros)
        
        # Filtro de búsqueda
        if buscar:
            termino = buscar.lower()
            moldes = [
                m for m in moldes 
                if termino in m.get('descripcion', '').lower() or 
                   termino in m.get('codigo', '').lower()
            ]
        
        return {
            "success": True,
            "total": len(moldes),
            "filtros_aplicados": {
                "estado": estado.value if estado else None,
                "activos_solo": activos_solo,
                "buscar": buscar
            },
            "moldes": moldes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listando moldes: {e}")
        return {
            "success": False,
            "error": str(e),
            "total": 0,
            "moldes": [],
            "message": "Error obteniendo moldes"
        }

@app.get("/colores", tags=["🎨 Colores"])
async def listar_colores(
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: ColorRepository = Depends(get_color_repo)
):
    """🎨 Listar todos los colores con formato optimizado para frontend"""
    try:
        colores = await repo.listar()
        
        if activos_solo:
            colores = [c for c in colores if c.get('activo', True)]
        
        if buscar:
            termino = buscar.lower()
            colores = [
                c for c in colores 
                if termino in c.get('nombre', '').lower() or 
                   termino in c.get('codigo', '').lower()
            ]
        
        return {
            "success": True,
            "total": len(colores),
            "filtros": {"activos_solo": activos_solo, "buscar": buscar},
            "colores": colores,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listando colores: {e}")
        return {
            "success": False,
            "error": str(e),
            "total": 0,
            "colores": [],
            "message": "Error obteniendo colores"
        }

# =====================================
# ENDPOINT DE PRUEBA CORS
# =====================================

@app.get("/test-cors", tags=["🔧 Testing"])
async def test_cors():
    """Endpoint de prueba para verificar que CORS funciona"""
    return {
        "message": "🎉 CORS funcionando correctamente!",
        "frontend_puede_conectar": True,
        "timestamp": datetime.now().isoformat(),
        "headers_cors": "Configurados correctamente"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema COMPLETO con CORS para React...")
    print("📍 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:3000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔗 CORS habilitado para conexión Frontend-Backend")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
