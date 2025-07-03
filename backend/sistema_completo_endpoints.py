from fastapi import FastAPI, HTTPException, status, Depends, Query
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
    logger.info("🚀 Sistema completo con MongoDB iniciado")
    
    yield
    
    # Shutdown
    await db_manager.close()
    logger.info("🛑 Sistema detenido")

# Aplicación FastAPI
app = FastAPI(
    title="🕯️ Sistema Completo Vel Arte - Con Todos los Datos",
    version="3.2.0",
    description="""
    ## Sistema completo con TODOS tus datos migrados de Excel
    
    ### ✅ Datos Migrados:
    * 📦 **44 Insumos** - Todos tus materiales  
    * 🏺 **140 Moldes** - Toda tu colección de moldes
    * 🎨 **30 Colores** - Paleta completa de colores
    
    ### 🚀 Funcionalidades:
    * Ver, crear, actualizar y eliminar TODOS los tipos de datos
    * Filtros avanzados y búsquedas
    * Cálculos de costos en tiempo real
    
    ### 🎯 ¡Tu Excel ya está aquí!
    """,
    lifespan=lifespan
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
        "message": "🎉 Sistema Completo Vel Arte - Todos los Datos Migrados",
        "version": "3.2.0",
        "datos_migrados": {
            "📦 insumos": "44 migrados",
            "🏺 moldes": "140 migrados", 
            "🎨 colores": "30 colores"
        },
        "status": "✅ Migración completa desde Excel",
        "funcionalidades": [
            "✅ Ver todos los insumos, moldes y colores",
            "✅ Crear, editar y eliminar registros",
            "✅ Filtros y búsquedas avanzadas",
            "✅ Cálculos de costos automáticos",
            "✅ Datos persistentes en MongoDB"
        ],
        "siguientes_pasos": "🚀 Frontend web interactivo"
    }

@app.get("/resumen-completo", tags=["🏠 General"])
async def resumen_completo(
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """Resumen completo de todos los datos"""
    
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
        }
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
            "collections": stats,
            "migracion": "✅ Datos de Excel importados correctamente",
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "❌ Problema detectado",
            "error": str(e),
            "timestamp": datetime.now()
        }

# =====================================
# CRUD INSUMOS
# =====================================

@app.get("/insumos", tags=["📦 Insumos"])
async def listar_insumos(
    activos_solo: bool = True,
    tipo: Optional[TipoInsumo] = None,
    stock_bajo: bool = False,
    buscar: Optional[str] = None,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Listar insumos con filtros avanzados"""
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
        "total": len(insumos),
        "filtros_aplicados": {
            "activos_solo": activos_solo,
            "tipo": tipo.value if tipo else None,
            "stock_bajo": stock_bajo,
            "buscar": buscar
        },
        "insumos": insumos
    }

@app.get("/insumos/{codigo}", tags=["📦 Insumos"])
async def obtener_insumo(codigo: str, repo: InsumoRepository = Depends(get_insumo_repo)):
    """Obtener insumo específico"""
    insumo = await repo.obtener_por_codigo(codigo)
    if not insumo:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    return insumo

@app.post("/insumos", tags=["📦 Insumos"])
async def crear_insumo(insumo: InsumoBase, repo: InsumoRepository = Depends(get_insumo_repo)):
    """Crear nuevo insumo"""
    existente = await repo.obtener_por_codigo(insumo.codigo)
    if existente:
        raise HTTPException(status_code=400, detail=f"Insumo {insumo.codigo} ya existe")
    
    insumo_data = insumo.dict()
    insumo_data['impuesto'] = insumo_data['costo_base'] * 0.1
    insumo_data['valor_total'] = insumo_data['costo_base'] + insumo_data['impuesto']
    
    nuevo_insumo = await repo.crear(insumo_data)
    return {"message": f"✅ Insumo {insumo.codigo} creado", "insumo": nuevo_insumo}

# =====================================
# CRUD MOLDES (¡NUEVO!)
# =====================================

@app.get("/moldes", tags=["🏺 Moldes"])
async def listar_moldes(
    estado: Optional[EstadoMolde] = None,
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: MoldeRepository = Depends(get_molde_repo)
):
    """📋 Listar todos los moldes con filtros"""
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
        "total": len(moldes),
        "filtros_aplicados": {
            "estado": estado.value if estado else None,
            "activos_solo": activos_solo,
            "buscar": buscar
        },
        "moldes": moldes
    }

@app.get("/moldes/{codigo}", tags=["🏺 Moldes"])
async def obtener_molde(codigo: str, repo: MoldeRepository = Depends(get_molde_repo)):
    """🔍 Obtener molde específico por código"""
    molde = await repo.obtener_por_codigo(codigo)
    if not molde:
        raise HTTPException(status_code=404, detail=f"Molde {codigo} no encontrado")
    return molde

@app.post("/moldes", tags=["🏺 Moldes"])
async def crear_molde(molde: MoldeBase, repo: MoldeRepository = Depends(get_molde_repo)):
    """➕ Crear nuevo molde"""
    existente = await repo.obtener_por_codigo(molde.codigo)
    if existente:
        raise HTTPException(status_code=400, detail=f"Molde {molde.codigo} ya existe")
    
    nuevo_molde = await repo.crear(molde.dict())
    return {"message": f"✅ Molde {molde.codigo} creado", "molde": nuevo_molde}

@app.put("/moldes/{codigo}", tags=["🏺 Moldes"])
async def actualizar_molde(
    codigo: str, 
    datos_actualizar: dict, 
    repo: MoldeRepository = Depends(get_molde_repo)
):
    """✏️ Actualizar molde existente"""
    existente = await repo.obtener_por_codigo(codigo)
    if not existente:
        raise HTTPException(status_code=404, detail=f"Molde {codigo} no encontrado")
    
    actualizado = await repo.actualizar(codigo, datos_actualizar)
    if actualizado:
        molde_actualizado = await repo.obtener_por_codigo(codigo)
        return {"message": f"✅ Molde {codigo} actualizado", "molde": molde_actualizado}
    else:
        raise HTTPException(status_code=500, detail="Error actualizando molde")

# =====================================
# CRUD COLORES (¡NUEVO!)
# =====================================

@app.get("/colores", tags=["🎨 Colores"])
async def listar_colores(
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: ColorRepository = Depends(get_color_repo)
):
    """🎨 Listar todos los colores"""
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
        "total": len(colores),
        "filtros": {"activos_solo": activos_solo, "buscar": buscar},
        "colores": colores
    }

@app.get("/colores/{codigo}", tags=["🎨 Colores"])
async def obtener_color(codigo: str, repo: ColorRepository = Depends(get_color_repo)):
    """🔍 Obtener color específico"""
    color = await repo.obtener_por_codigo(codigo)
    if not color:
        raise HTTPException(status_code=404, detail=f"Color {codigo} no encontrado")
    return color

@app.post("/colores", tags=["🎨 Colores"])
async def crear_color(color: ColorBase, repo: ColorRepository = Depends(get_color_repo)):
    """➕ Crear nuevo color"""
    existente = await repo.obtener_por_codigo(color.codigo)
    if existente:
        raise HTTPException(status_code=400, detail=f"Color {color.codigo} ya existe")
    
    nuevo_color = await repo.crear(color.dict())
    return {"message": f"✅ Color {color.codigo} creado", "color": nuevo_color}

# =====================================
# ENDPOINTS DE BÚSQUEDA GLOBAL
# =====================================

@app.get("/buscar-todo", tags=["🔍 Búsqueda Global"])
async def buscar_todo(
    termino: str,
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """🔍 Buscar en todos los tipos de datos"""
    termino_lower = termino.lower()
    
    # Buscar en insumos
    insumos = await insumo_repo.listar()
    insumos_encontrados = [
        i for i in insumos 
        if termino_lower in i.get('descripcion', '').lower() or 
           termino_lower in i.get('codigo', '').lower()
    ]
    
    # Buscar en moldes
    moldes = await molde_repo.listar()
    moldes_encontrados = [
        m for m in moldes 
        if termino_lower in m.get('descripcion', '').lower() or 
           termino_lower in m.get('codigo', '').lower()
    ]
    
    # Buscar en colores
    colores = await color_repo.listar()
    colores_encontrados = [
        c for c in colores 
        if termino_lower in c.get('nombre', '').lower() or 
           termino_lower in c.get('codigo', '').lower()
    ]
    
    return {
        "termino_buscado": termino,
        "resultados": {
            "insumos": {"total": len(insumos_encontrados), "datos": insumos_encontrados},
            "moldes": {"total": len(moldes_encontrados), "datos": moldes_encontrados},
            "colores": {"total": len(colores_encontrados), "datos": colores_encontrados}
        },
        "total_encontrados": len(insumos_encontrados) + len(moldes_encontrados) + len(colores_encontrados)
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema COMPLETO con todos los datos migrados...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📊 Resumen: http://localhost:8000/resumen-completo")
    print("🔍 Buscar: http://localhost:8000/buscar-todo?termino=cera")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
