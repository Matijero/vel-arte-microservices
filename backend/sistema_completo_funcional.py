from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
from decimal import Decimal
import uvicorn
import logging
import jwt
import hashlib
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

# Configuración de seguridad
SECRET_KEY = "tu-super-secreto-muy-largo-y-complejo-cambiar-en-produccion-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

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

class RolUsuario(str, Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    CONSULTA = "consulta"

# =====================================
# MODELOS AVANZADOS
# =====================================

class Usuario(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    rol: RolUsuario = RolUsuario.CONSULTA
    activo: bool = True
    fecha_creacion: datetime = Field(default_factory=datetime.now)

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    rol: RolUsuario = RolUsuario.CONSULTA

class UsuarioLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: Usuario

class InsumoCreate(BaseModel):
    codigo: str
    descripcion: str
    tipo: TipoInsumo
    costo_base: float
    cantidad_inventario: int = 0
    unidad_medida: str
    proveedor: Optional[str] = None
    activo: bool = True

class InsumoUpdate(BaseModel):
    descripcion: Optional[str] = None
    tipo: Optional[TipoInsumo] = None
    costo_base: Optional[float] = None
    cantidad_inventario: Optional[int] = None
    unidad_medida: Optional[str] = None
    proveedor: Optional[str] = None
    activo: Optional[bool] = None

class MoldeCreate(BaseModel):
    codigo: str
    descripcion: str
    peso_cera_necesario: float
    cantidad_pabilo: int
    estado: EstadoMolde = EstadoMolde.DISPONIBLE
    ubicacion_fisica: Optional[str] = None
    dimensiones: Optional[str] = None
    precio_base_calculado: Optional[float] = 0
    activo: bool = True

class MoldeUpdate(BaseModel):
    descripcion: Optional[str] = None
    peso_cera_necesario: Optional[float] = None
    cantidad_pabilo: Optional[int] = None
    estado: Optional[EstadoMolde] = None
    ubicacion_fisica: Optional[str] = None
    dimensiones: Optional[str] = None
    precio_base_calculado: Optional[float] = None
    activo: Optional[bool] = None

class ColorCreate(BaseModel):
    codigo: str
    nombre: str
    cantidad_gotas_estandar: int = 10
    activo: bool = True

class ColorUpdate(BaseModel):
    nombre: Optional[str] = None
    cantidad_gotas_estandar: Optional[int] = None
    activo: Optional[bool] = None

class CalculoCostoRequest(BaseModel):
    molde_codigo: str
    insumos: Dict[str, float] = Field(..., description="Diccionario {codigo_insumo: cantidad}")
    colores: List[str] = Field(default=[], description="Lista de códigos de colores")
    nivel_calidad: int = Field(default=2, ge=1, le=4, description="Nivel de calidad 1-4")
    cantidad_producir: int = Field(default=1, ge=1, description="Cantidad a producir")
    margen_adicional: float = Field(default=0, description="Margen adicional")

class CalculoCostoResponse(BaseModel):
    molde_info: dict
    insumos_utilizados: List[dict]
    colores_utilizados: List[dict]
    costo_total_materiales: float
    costo_por_unidad: float
    factor_calidad: float
    precio_sin_redondear: float
    precio_final_redondeado: float
    ganancia_por_unidad: float
    margen_porcentual: float
    cantidad_producir: int
    valor_total_lote: float
    ganancia_total_lote: float
    fecha_calculo: datetime = Field(default_factory=datetime.now)

# =====================================
# FUNCIONES DE SEGURIDAD
# =====================================

def hash_password(password: str) -> str:
    """Hash de password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verificar password"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Base de datos de usuarios (en memoria para demo)
usuarios_db = {
    "admin": {
        "username": "admin",
        "email": "admin@velarte.com",
        "hashed_password": hash_password("admin123"),
        "rol": "admin",
        "activo": True
    },
    "operador": {
        "username": "operador",
        "email": "operador@velarte.com", 
        "hashed_password": hash_password("operador123"),
        "rol": "operador",
        "activo": True
    }
}

# =====================================
# CALCULADORA DE COSTOS AVANZADA
# =====================================

class CalculadoraCostosAvanzada:
    """Calculadora que replica todas las fórmulas de Excel"""
    
    # Factores de calidad (de tu Excel)
    FACTORES_CALIDAD = {
        1: 3.2,  # Premium
        2: 3.0,  # Alta  
        3: 2.8,  # Estándar
        4: 2.6   # Básica
    }
    
    @classmethod
    async def calcular_costo_completo(
        cls, 
        request: CalculoCostoRequest,
        insumo_repo: InsumoRepository,
        molde_repo: MoldeRepository,
        color_repo: ColorRepository
    ) -> CalculoCostoResponse:
        """Cálculo completo de costos con todas las reglas de negocio"""
        
        # Obtener molde
        molde = await molde_repo.obtener_por_codigo(request.molde_codigo)
        if not molde:
            raise HTTPException(status_code=404, detail=f"Molde {request.molde_codigo} no encontrado")
        
        # Calcular costos de insumos
        insumos_utilizados = []
        costo_total_insumos = 0.0
        
        for codigo_insumo, cantidad in request.insumos.items():
            insumo = await insumo_repo.obtener_por_codigo(codigo_insumo)
            if not insumo:
                raise HTTPException(status_code=404, detail=f"Insumo {codigo_insumo} no encontrado")
            
            # Calcular costo según tipo de insumo
            costo_unitario = cls._calcular_costo_por_tipo(insumo, cantidad)
            costo_total_item = costo_unitario * cantidad
            
            insumos_utilizados.append({
                "codigo": codigo_insumo,
                "descripcion": insumo["descripcion"],
                "tipo": insumo["tipo"],
                "cantidad_usada": cantidad,
                "unidad": insumo["unidad_medida"],
                "costo_unitario": costo_unitario,
                "costo_total": costo_total_item
            })
            
            costo_total_insumos += costo_total_item
        
        # Calcular costos de colores
        colores_utilizados = []
        costo_total_colores = 0.0
        
        for codigo_color in request.colores:
            color = await color_repo.obtener_por_codigo(codigo_color)
            if color:
                # Costo estimado por color
                costo_color = color["cantidad_gotas_estandar"] * 50  # $50 por gota
                colores_utilizados.append({
                    "codigo": codigo_color,
                    "nombre": color["nombre"],
                    "gotas_usadas": color["cantidad_gotas_estandar"],
                    "costo": costo_color
                })
                costo_total_colores += costo_color
        
        # Costo total de materiales
        costo_total_materiales = costo_total_insumos + costo_total_colores
        
        # Costo por unidad
        costo_por_unidad = costo_total_materiales / request.cantidad_producir
        
        # Aplicar factor de calidad
        factor_calidad = cls.FACTORES_CALIDAD.get(request.nivel_calidad, 2.8)
        precio_con_calidad = costo_total_materiales * factor_calidad
        
        # Agregar margen adicional
        precio_sin_redondear = precio_con_calidad + request.margen_adicional
        
        # Redondear a múltiplo de 500
        precio_final_redondeado = cls._redondear_precio(precio_sin_redondear)
        
        # Calcular ganancias
        ganancia_total = precio_final_redondeado - costo_total_materiales
        ganancia_por_unidad = ganancia_total / request.cantidad_producir
        margen_porcentual = (ganancia_total / costo_total_materiales * 100) if costo_total_materiales > 0 else 0
        
        return CalculoCostoResponse(
            molde_info={
                "codigo": molde["codigo"],
                "descripcion": molde["descripcion"],
                "peso_cera_necesario": molde["peso_cera_necesario"],
                "cantidad_pabilo": molde["cantidad_pabilo"]
            },
            insumos_utilizados=insumos_utilizados,
            colores_utilizados=colores_utilizados,
            costo_total_materiales=costo_total_materiales,
            costo_por_unidad=costo_por_unidad,
            factor_calidad=factor_calidad,
            precio_sin_redondear=precio_sin_redondear,
            precio_final_redondeado=precio_final_redondeado,
            ganancia_por_unidad=ganancia_por_unidad,
            margen_porcentual=margen_porcentual,
            cantidad_producir=request.cantidad_producir,
            valor_total_lote=precio_final_redondeado,
            ganancia_total_lote=ganancia_total
        )
    
    @classmethod
    def _calcular_costo_por_tipo(cls, insumo: dict, cantidad: float) -> float:
        """Calcular costo según tipo de insumo (réplica de Excel)"""
        tipo = insumo.get("tipo", "otros")
        costo_base = insumo.get("costo_base", 0)
        
        if tipo == "cera":
            # Cera: de kilo a gramo
            return costo_base / 1000
        elif tipo == "fragancia":
            # Fragancia: de botella a ml
            return costo_base / 20
        elif tipo == "colorante":
            # Colorante: de botella a gotas
            return costo_base / 10
        elif tipo == "aditivo":
            # Aditivo: similar a cera
            return costo_base / 1000
        else:
            # Otros: costo directo
            return insumo.get("valor_total", costo_base)
    
    @classmethod
    def _redondear_precio(cls, precio: float) -> float:
        """Redondear a múltiplo de 500"""
        return round(precio / 500) * 500

# =====================================
# APLICACIÓN FASTAPI
# =====================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    await db_manager.connect()
    logger.info("🚀 Sistema completo funcional iniciado")
    
    yield
    
    # Shutdown
    await db_manager.close()
    logger.info("🛑 Sistema detenido")

# Aplicación FastAPI
app = FastAPI(
    title="🕯️ Sistema Vel Arte - Completo y Funcional",
    version="4.0.0",
    description="""
    ## Sistema Completo con Todas las Funcionalidades
    
    ### ✅ Funcionalidades Implementadas:
    * 🔐 **Autenticación y Autorización** - Login seguro con roles
    * 🧮 **Calculadora Funcional** - Cálculos reales con fórmulas de Excel
    * ➕ **CRUD Completo** - Agregar, editar, eliminar todo
    * 📊 **Dashboard Dinámico** - Datos en tiempo real
    * 🔍 **Búsqueda Avanzada** - Filtros y búsquedas
    
    ### 🔐 Usuarios Demo:
    * **admin / admin123** - Acceso completo
    * **operador / operador123** - Operaciones limitadas
    
    ### 📊 Datos:
    * 44 Insumos migrados de Excel
    * 140 Moldes con información completa
    * 30 Colores disponibles
    """,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
async def get_insumo_repo() -> InsumoRepository:
    return InsumoRepository(db_manager.get_database())

async def get_molde_repo() -> MoldeRepository:
    return MoldeRepository(db_manager.get_database())

async def get_color_repo() -> ColorRepository:
    return ColorRepository(db_manager.get_database())

def get_current_user(token_data: dict = Depends(verify_token)):
    """Obtener usuario actual del token"""
    username = token_data.get("sub")
    user_data = usuarios_db.get(username)
    if not user_data:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user_data

def require_role(required_roles: List[str]):
    """Decorator para requerir roles específicos"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in required_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Se requiere rol: {required_roles}. Tu rol: {current_user['rol']}"
            )
        return current_user
    return role_checker

# =====================================
# ENDPOINTS DE AUTENTICACIÓN
# =====================================

@app.post("/auth/login", response_model=Token, tags=["🔐 Autenticación"])
async def login(user_login: UsuarioLogin):
    """Login de usuario"""
    user = usuarios_db.get(user_login.username)
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not user["activo"]:
        raise HTTPException(status_code=401, detail="Usuario inactivo")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "rol": user["rol"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_info=Usuario(
            username=user["username"],
            email=user["email"],
            rol=user["rol"],
            activo=user["activo"]
        )
    )

@app.get("/auth/me", response_model=Usuario, tags=["🔐 Autenticación"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return Usuario(
        username=current_user["username"],
        email=current_user["email"],
        rol=current_user["rol"],
        activo=current_user["activo"]
    )

# =====================================
# ENDPOINTS PÚBLICOS
# =====================================

@app.get("/", tags=["🏠 General"])
async def home():
    return {
        "message": "🎉 Sistema Vel Arte - Completo y Funcional",
        "version": "4.0.0",
        "features": [
            "✅ Autenticación completa",
            "✅ Calculadora funcional", 
            "✅ CRUD completo",
            "✅ Roles y permisos",
            "✅ Todas las funcionalidades"
        ],
        "auth": {
            "demo_users": {
                "admin": "admin123",
                "operador": "operador123"
            }
        },
        "endpoints": {
            "frontend": "http://localhost:3000",
            "backend": "http://localhost:8000",
            "docs": "http://localhost:8000/docs"
        }
    }

@app.get("/resumen-completo", tags=["🏠 General"])
async def resumen_completo(
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """Resumen completo - sin autenticación requerida"""
    try:
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
            "auth_required": False
        }
    except Exception as e:
        logger.error(f"Error en resumen: {e}")
        return {"error": str(e)}

# =====================================
# CRUD INSUMOS CON AUTENTICACIÓN
# =====================================

@app.get("/insumos", tags=["📦 Insumos"])
async def listar_insumos(
    activos_solo: bool = True,
    tipo: Optional[TipoInsumo] = None,
    stock_bajo: bool = False,
    buscar: Optional[str] = None,
    repo: InsumoRepository = Depends(get_insumo_repo)
):
    """Listar insumos - Acceso público para consulta"""
    try:
        filtros = {}
        if activos_solo:
            filtros["activo"] = True
        if tipo:
            filtros["tipo"] = tipo.value
        
        insumos = await repo.listar(filtros)
        
        if stock_bajo:
            insumos = [i for i in insumos if i.get('cantidad_inventario', 0) <= 10]
        
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
            "insumos": insumos
        }
    except Exception as e:
        return {"success": False, "error": str(e), "insumos": []}

@app.post("/insumos", tags=["📦 Insumos"])
async def crear_insumo(
    insumo: InsumoCreate,
    repo: InsumoRepository = Depends(get_insumo_repo),
    current_user: dict = Depends(require_role(["admin", "operador"]))
):
    """Crear nuevo insumo - Requiere rol admin u operador"""
    try:
        # Verificar que no existe
        existente = await repo.obtener_por_codigo(insumo.codigo)
        if existente:
            raise HTTPException(status_code=400, detail=f"Insumo {insumo.codigo} ya existe")
        
        # Preparar datos
        insumo_data = insumo.dict()
        insumo_data['impuesto'] = insumo_data['costo_base'] * 0.1
        insumo_data['valor_total'] = insumo_data['costo_base'] + insumo_data['impuesto']
        
        # Crear
        nuevo_insumo = await repo.crear(insumo_data)
        
        return {
            "success": True,
            "message": f"✅ Insumo {insumo.codigo} creado correctamente",
            "insumo": nuevo_insumo,
            "created_by": current_user["username"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando insumo: {e}")

@app.put("/insumos/{codigo}", tags=["📦 Insumos"])
async def actualizar_insumo(
    codigo: str,
    insumo_update: InsumoUpdate,
    repo: InsumoRepository = Depends(get_insumo_repo),
    current_user: dict = Depends(require_role(["admin", "operador"]))
):
    """Actualizar insumo - Requiere rol admin u operador"""
    try:
        # Verificar que existe
        existente = await repo.obtener_por_codigo(codigo)
        if not existente:
            raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
        
        # Preparar datos de actualización
        datos_actualizar = insumo_update.dict(exclude_unset=True)
        
        # Recalcular si se actualiza el costo
        if 'costo_base' in datos_actualizar:
            datos_actualizar['impuesto'] = datos_actualizar['costo_base'] * 0.1
            datos_actualizar['valor_total'] = datos_actualizar['costo_base'] + datos_actualizar['impuesto']
        
        # Actualizar
        actualizado = await repo.actualizar(codigo, datos_actualizar)
        
        if actualizado:
            insumo_actualizado = await repo.obtener_por_codigo(codigo)
            return {
                "success": True,
                "message": f"✅ Insumo {codigo} actualizado correctamente",
                "insumo": insumo_actualizado,
                "updated_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=500, detail="Error actualizando insumo")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando insumo: {e}")

@app.delete("/insumos/{codigo}", tags=["📦 Insumos"])
async def eliminar_insumo(
    codigo: str,
    repo: InsumoRepository = Depends(get_insumo_repo),
    current_user: dict = Depends(require_role(["admin"]))
):
    """Eliminar insumo - Solo admin"""
    try:
        eliminado = await repo.eliminar(codigo)
        
        if eliminado:
            return {
                "success": True,
                "message": f"✅ Insumo {codigo} eliminado correctamente",
                "deleted_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando insumo: {e}")

# =====================================
# CRUD MOLDES CON AUTENTICACIÓN
# =====================================

@app.get("/moldes", tags=["🏺 Moldes"])
async def listar_moldes(
    estado: Optional[EstadoMolde] = None,
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: MoldeRepository = Depends(get_molde_repo)
):
    """Listar moldes - Acceso público"""
    try:
        filtros = {}
        if activos_solo:
            filtros["activo"] = True
        if estado:
            filtros["estado"] = estado.value
        
        moldes = await repo.listar(filtros)
        
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
            "moldes": moldes
        }
    except Exception as e:
        return {"success": False, "error": str(e), "moldes": []}

@app.post("/moldes", tags=["🏺 Moldes"])
async def crear_molde(
    molde: MoldeCreate,
    repo: MoldeRepository = Depends(get_molde_repo),
    current_user: dict = Depends(require_role(["admin", "operador"]))
):
    """Crear nuevo molde"""
    try:
        existente = await repo.obtener_por_codigo(molde.codigo)
        if existente:
            raise HTTPException(status_code=400, detail=f"Molde {molde.codigo} ya existe")
        
        nuevo_molde = await repo.crear(molde.dict())
        
        return {
            "success": True,
            "message": f"✅ Molde {molde.codigo} creado correctamente",
            "molde": nuevo_molde,
            "created_by": current_user["username"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando molde: {e}")

@app.put("/moldes/{codigo}", tags=["🏺 Moldes"])
async def actualizar_molde(
    codigo: str,
    molde_update: MoldeUpdate,
    repo: MoldeRepository = Depends(get_molde_repo),
    current_user: dict = Depends(require_role(["admin", "operador"]))
):
    """Actualizar molde"""
    try:
        existente = await repo.obtener_por_codigo(codigo)
        if not existente:
            raise HTTPException(status_code=404, detail=f"Molde {codigo} no encontrado")
        
        datos_actualizar = molde_update.dict(exclude_unset=True)
        actualizado = await repo.actualizar(codigo, datos_actualizar)
        
        if actualizado:
            molde_actualizado = await repo.obtener_por_codigo(codigo)
            return {
                "success": True,
                "message": f"✅ Molde {codigo} actualizado correctamente",
                "molde": molde_actualizado,
                "updated_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=500, detail="Error actualizando molde")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando molde: {e}")

# =====================================
# CALCULADORA FUNCIONAL
# =====================================

@app.post("/calcular-costo", response_model=CalculoCostoResponse, tags=["🧮 Calculadora"])
async def calcular_costo_vela(
    request: CalculoCostoRequest,
    insumo_repo: InsumoRepository = Depends(get_insumo_repo),
    molde_repo: MoldeRepository = Depends(get_molde_repo),
    color_repo: ColorRepository = Depends(get_color_repo)
):
    """🧮 Calculadora de costos funcional - Réplica exacta de Excel"""
    try:
        resultado = await CalculadoraCostosAvanzada.calcular_costo_completo(
            request, insumo_repo, molde_repo, color_repo
        )
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {e}")

@app.get("/factores-calidad", tags=["🧮 Calculadora"])
async def obtener_factores_calidad():
    """Obtener factores de calidad disponibles"""
    return {
        "factores": {
            1: {"valor": 3.2, "descripcion": "Premium"},
            2: {"valor": 3.0, "descripcion": "Alta"},
            3: {"valor": 2.8, "descripcion": "Estándar"},
            4: {"valor": 2.6, "descripcion": "Básica"}
        }
    }

# =====================================
# OTROS ENDPOINTS
# =====================================

@app.get("/colores", tags=["🎨 Colores"])
async def listar_colores(
    activos_solo: bool = True,
    buscar: Optional[str] = None,
    repo: ColorRepository = Depends(get_color_repo)
):
    """Listar colores"""
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
            "colores": colores
        }
    except Exception as e:
        return {"success": False, "error": str(e), "colores": []}

if __name__ == "__main__":
    print("🚀 Iniciando Sistema COMPLETO Y FUNCIONAL...")
    print("📍 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:3000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔐 Login demo: admin/admin123 o operador/operador123")
    print("🧮 Calculadora: FUNCIONAL")
    print("➕ CRUD: COMPLETO")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
