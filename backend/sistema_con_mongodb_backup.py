from fastapi import FastAPI, HTTPException, status, Depends
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

# Enums y modelos básicos (los mismos de antes)
from enum import Enum

class TipoInsumo(str, Enum):
    CERA = "cera"
    FRAGANCIA = "fragancia" 
    COLORANTE = "colorante"
    PABILO = "pabilo"
    ADITIVO = "aditivo"
    OTROS = "otros"

class EstadoMolde(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"

# Modelos Pydantic simplificados para empezar
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
    logger.info("🚀 Sistema con MongoDB iniciado")
    
    yield
    
    # Shutdown
    await db_manager.close()
    logger.info("🛑 Sistema detenido")

# Aplicación FastAPI
app = FastAPI(
    title="🕯️ Sistema Vel Arte con MongoDB",
    version="3.1.0",
    description="Sistema conectado a base de datos persistente",
    lifespan=lifespan
)

# Dependencias
async def get_insumo_repo() -> InsumoRepository:
    """Obtener repositorio de insumos"""
    return InsumoRepository(db_manager.get_database())

async def get_molde_repo() -> MoldeRepository:
    """Obtener repositorio de moldes"""
    return MoldeRepository(db_manager.get_database())

async def get_color_repo() -> ColorRepository:
    """Obtener repositorio de colores"""
    return ColorRepository(db_manager.get_database())

# =====================================
# ENDPOINTS PRINCIPALES
# =====================================

@app.get("/", tags=["🏠 General"])
async def home():
    return {
        "message": "🎉 Sistema Vel Arte con MongoDB funcionando",
        "version": "3.1.0",
        "database": "✅ MongoDB conectado",
        "status": "✅ Datos persistentes",
        "cambios": [
            "✅ Datos se guardan en MongoDB",
            "✅ No se pierden al reiniciar",
            "✅ Consultas optimizadas",
            "✅ Índices para mejor rendimiento"
        ]
    }

@app.get("/health", tags=["🏠 General"])
async def health_check():
    """Verificar estado del sistema y base de datos"""
    try:
        # Verificar conexión a MongoDB
        await db_manager.client.admin.command('ping')
        
        # Contar documentos en colecciones
        db = db_manager.get_database()
        stats = {
            "insumos": await db.insumos.count_documents({}),
            "moldes": await db.moldes.count_documents({}),
            "colores": await db.colores.count_documents({})
        }
        
        return {
            "status": "✅ Sistema saludable",
            "database": "✅ MongoDB conectado",
            "collections": stats,
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "❌ Problema detectado",
            "error": str(e),
            "timestamp": datetime.now()
        }

# =====================================
# CRUD INSUMOS CON MONGODB
# =====================================

@app.get("/insumos", tags=["📦 Insumos MongoDB"])
async def listar_insumos(
    activos_solo: bool = True,
    tipo: Optional[TipoInsumo] = None,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Listar insumos desde MongoDB"""
    filtros = {}
    
    if activos_solo:
        filtros["activo"] = True
    
    if tipo:
        filtros["tipo"] = tipo.value
    
    insumos = await repo.listar(filtros)
    return {
        "total": len(insumos),
        "filtros_aplicados": filtros,
        "insumos": insumos
    }

@app.get("/insumos/{codigo}", tags=["📦 Insumos MongoDB"])
async def obtener_insumo(
    codigo: str,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Obtener insumo específico desde MongoDB"""
    insumo = await repo.obtener_por_codigo(codigo)
    
    if not insumo:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    
    return insumo

@app.post("/insumos", tags=["📦 Insumos MongoDB"])
async def crear_insumo(
    insumo: InsumoBase,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Crear nuevo insumo en MongoDB"""
    
    # Verificar que no existe
    existente = await repo.obtener_por_codigo(insumo.codigo)
    if existente:
        raise HTTPException(status_code=400, detail=f"Insumo {insumo.codigo} ya existe")
    
    # Calcular valores automáticos
    insumo_data = insumo.dict()
    insumo_data['impuesto'] = insumo_data['costo_base'] * 0.1
    insumo_data['valor_total'] = insumo_data['costo_base'] + insumo_data['impuesto']
    
    # Crear en base de datos
    nuevo_insumo = await repo.crear(insumo_data)
    
    return {
        "message": f"✅ Insumo {insumo.codigo} creado en MongoDB",
        "insumo": nuevo_insumo
    }

@app.put("/insumos/{codigo}", tags=["📦 Insumos MongoDB"])
async def actualizar_insumo(
    codigo: str,
    datos_actualizar: dict,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Actualizar insumo en MongoDB"""
    
    # Verificar que existe
    existente = await repo.obtener_por_codigo(codigo)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    
    # Recalcular valores si se actualiza el costo
    if 'costo_base' in datos_actualizar:
        datos_actualizar['impuesto'] = datos_actualizar['costo_base'] * 0.1
        datos_actualizar['valor_total'] = datos_actualizar['costo_base'] + datos_actualizar['impuesto']
    
    # Actualizar en base de datos
    actualizado = await repo.actualizar(codigo, datos_actualizar)
    
    if actualizado:
        insumo_actualizado = await repo.obtener_por_codigo(codigo)
        return {
            "message": f"✅ Insumo {codigo} actualizado en MongoDB",
            "insumo": insumo_actualizado
        }
    else:
        raise HTTPException(status_code=500, detail="Error actualizando insumo")

@app.delete("/insumos/{codigo}", tags=["📦 Insumos MongoDB"])
async def eliminar_insumo(
    codigo: str,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Eliminar insumo de MongoDB"""
    
    eliminado = await repo.eliminar(codigo)
    
    if eliminado:
        return {"message": f"✅ Insumo {codigo} eliminado de MongoDB"}
    else:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")

# =====================================
# ENDPOINTS DE PRUEBA INICIALES
# =====================================

@app.post("/poblar-datos-iniciales", tags=["🔧 Configuración"])
async def poblar_datos_iniciales(
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """Poblar la base de datos con datos iniciales para pruebas"""
    
    # Datos iniciales de insumos
    insumos_iniciales = [
        {
            "codigo": "CV001",
            "descripcion": "CERA DE VASO",
            "tipo": "cera",
            "costo_base": 28000,
            "cantidad_inventario": 50,
            "unidad_medida": "kg",
            "proveedor": "Proveedor Ceras S.A.",
            "activo": True,
            "impuesto": 2800,
            "valor_total": 30800
        },
        {
            "codigo": "FR001", 
            "descripcion": "FRAGANCIA PREMIUM",
            "tipo": "fragancia",
            "costo_base": 6000,
            "cantidad_inventario": 20,
            "unidad_medida": "ml",
            "proveedor": "Aromas Naturales",
            "activo": True,
            "impuesto": 600,
            "valor_total": 6600
        }
    ]
    
    # Crear insumos si no existen
    insumos_creados = 0
    for insumo_data in insumos_iniciales:
        existente = await insumo_repo.obtener_por_codigo(insumo_data["codigo"])
        if not existente:
            await insumo_repo.crear(insumo_data)
            insumos_creados += 1
    
    return {
        "message": "✅ Datos iniciales poblados",
        "insumos_creados": insumos_creados,
        "resultado": "Base de datos lista para usar"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema Vel Arte con MongoDB...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("💾 Database: MongoDB persistente")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
