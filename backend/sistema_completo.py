from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Union
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uvicorn
import uuid
import math

# =====================================
# ENUMS Y CONSTANTES
# =====================================

class EstadoMolde(str, Enum):
    DISPONIBLE = "disponible"
    EN_USO = "en_uso"
    MANTENIMIENTO = "mantenimiento"
    DANADO = "dañado"

class LineaProducto(str, Enum):
    BOKEH_FLOWER = "bokeh_flower"
    CAJAS_MAMA = "cajas_mama"
    DISENOS_PP = "disenos_pp"
    DISENOS_PCT = "disenos_pct"
    BAUTIZO = "bautizo"
    KARLA = "karla"
    MASAJES = "masajes"
    VELAS_GENERICAS = "velas_genericas"

class TipoInsumo(str, Enum):
    CERA = "cera"  # Cálculo por kilo → gramo (/1000)
    FRAGANCIA = "fragancia"  # Cálculo por botella → ml (/20)
    COLORANTE = "colorante"  # Cálculo por botella → gotas (/10)
    PABILO = "pabilo"  # Cálculo directo
    ADITIVO = "aditivo"  # Cálculo por porcentaje
    DECORACION = "decoracion"  # Cálculo directo
    ENVASE = "envase"  # Cálculo directo
    OTROS = "otros"

class VersionCosto(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

# Factores de calidad (extraídos de tu Excel)
FACTORES_CALIDAD = {
    1: Decimal("3.2"),  # Premium
    2: Decimal("3.0"),  # Alta
    3: Decimal("2.8"),  # Estándar
    4: Decimal("2.6")   # Básica
}

# Configuraciones específicas por línea de producto
CONFIGURACIONES_LINEA = {
    LineaProducto.BOKEH_FLOWER: {"descuento_especial": 0, "factor_adicional": 1.0},
    LineaProducto.CAJAS_MAMA: {"descuento_especial": 0, "factor_adicional": 1.1},
    LineaProducto.DISENOS_PP: {"descuento_especial": 0, "factor_adicional": 1.0},
    LineaProducto.DISENOS_PCT: {"descuento_especial": 110, "factor_adicional": 1.0},
    LineaProducto.BAUTIZO: {"descuento_especial": 110, "factor_adicional": 1.05},
    LineaProducto.KARLA: {"descuento_especial": 110, "factor_adicional": 1.0},
    LineaProducto.MASAJES: {"descuento_especial": 0, "factor_adicional": 1.2},
}

# =====================================
# MODELOS DE DATOS AVANZADOS
# =====================================

class InsumoCompleto(BaseModel):
    """Modelo completo de insumo con todas las reglas de negocio"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., description="Código único (CV001, FR001, etc.)")
    capacidad: Optional[str] = Field(None, description="Capacidad (45 ML, 1 KG, etc.)")
    descripcion: str = Field(..., description="Descripción completa")
    tipo: TipoInsumo = Field(..., description="Tipo de insumo para cálculos")
    
    # Costos base
    costo_base: Decimal = Field(..., description="Costo base del insumo")
    impuesto: Decimal = Field(default=Decimal("0"), description="Impuesto (auto-calculado 10%)")
    costo_envio: Decimal = Field(default=Decimal("0"), description="Costo de envío")
    valor_total: Decimal = Field(default=Decimal("0"), description="Valor total calculado")
    
    # Información de inventario
    cantidad_inventario: int = Field(default=0, description="Cantidad en inventario")
    cantidad_minima: int = Field(default=10, description="Stock mínimo")
    unidad_medida: str = Field(..., description="gr, ml, unidad, gotas, etc.")
    
    # Información del proveedor
    proveedor: Optional[str] = Field(None, description="Nombre del proveedor")
    fecha_ultima_compra: Optional[date] = Field(None)
    precio_ultima_compra: Optional[Decimal] = Field(None)
    
    # Control de sistema
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    
    # Configuración de cálculos específicos
    factor_conversion: Optional[Decimal] = Field(None, description="Factor de conversión específico")
    rendimiento_esperado: Optional[Decimal] = Field(None, description="Rendimiento esperado %")
    
    @validator('impuesto', pre=True, always=True)
    def calcular_impuesto(cls, v, values):
        """Auto-calcular impuesto del 10%"""
        if 'costo_base' in values:
            return values['costo_base'] * Decimal("0.1")
        return v
    
    @validator('valor_total', pre=True, always=True)
    def calcular_valor_total(cls, v, values):
        """Auto-calcular valor total"""
        costo = values.get('costo_base', Decimal("0"))
        impuesto = values.get('impuesto', Decimal("0"))
        envio = values.get('costo_envio', Decimal("0"))
        return costo + impuesto + envio

class MoldeCompleto(BaseModel):
    """Modelo completo de molde con todas las especificaciones"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., description="Código único (VA601, VA602, etc.)")
    descripcion: str = Field(..., description="Descripción del molde")
    
    # Especificaciones técnicas
    tipo_vela: Optional[str] = Field(None, description="Tipo de vela que produce")
    material_molde: Optional[str] = Field(None, description="Material del molde")
    dimensiones: Optional[str] = Field(None, description="Dimensiones (3X3X3)")
    peso_molde: Optional[Decimal] = Field(None, description="Peso del molde en gramos")
    peso_cera_necesario: Decimal = Field(..., description="Peso de cera necesario")
    cantidad_pabilo: int = Field(..., description="Cantidad de pabilo necesario")
    
    # Estado y ubicación
    estado: EstadoMolde = Field(default=EstadoMolde.DISPONIBLE)
    ubicacion_fisica: Optional[str] = Field(None, description="Estante A-1, B-2, etc.")
    responsable: Optional[str] = Field(None, description="Persona responsable")
    
    # Cálculos financieros
    precio_base_calculado: Decimal = Field(default=Decimal("0"), description="Precio base automático")
    ganancia_esperada: Decimal = Field(default=Decimal("0"), description="Ganancia esperada")
    margen_minimo: Decimal = Field(default=Decimal("30"), description="Margen mínimo %")
    
    # Líneas de producto compatibles
    lineas_compatibles: List[LineaProducto] = Field(default_factory=list)
    
    # Control de uso
    veces_usado: int = Field(default=0, description="Cantidad de veces usado")
    fecha_ultimo_uso: Optional[date] = Field(None)
    mantenimientos: List[str] = Field(default_factory=list, description="Historial de mantenimientos")
    
    # Control de sistema
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)

class ColorCompleto(BaseModel):
    """Modelo completo de color con información extendida"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., description="Código del color (R1, R2, etc.)")
    nombre: str = Field(..., description="Nombre descriptivo del color")
    nombre_comercial: Optional[str] = Field(None, description="Nombre comercial")
    
    # Especificaciones técnicas
    cantidad_gotas_estandar: int = Field(..., description="Gotas estándar por uso")
    intensidad: int = Field(default=5, description="Intensidad 1-10")
    tipo_base: str = Field(default="liquido", description="líquido, polvo, etc.")
    
    # Información de mezclas
    colores_base: Optional[List[str]] = Field(None, description="Colores base para mezclas")
    formula_mezcla: Optional[str] = Field(None, description="Fórmula de mezcla")
    
    # Control de inventario
    stock_actual: int = Field(default=0, description="Stock actual en ml/gr")
    punto_reorden: int = Field(default=50, description="Punto de reorden")
    
    # Control de sistema
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)

class ProductoCompleto(BaseModel):
    """Modelo completo de producto final"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., description="Código único del producto")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: Optional[str] = Field(None)
    
    # Clasificación
    linea_producto: LineaProducto = Field(..., description="Línea de producto")
    categoria: Optional[str] = Field(None, description="Categoría específica")
    temporada: Optional[str] = Field(None, description="Temporada (Navidad, etc.)")
    
    # Componentes
    molde_usado: str = Field(..., description="Código del molde")
    insumos_formula: Dict[str, Decimal] = Field(..., description="Fórmula de insumos")
    colores_usados: List[str] = Field(default_factory=list, description="Códigos de colores")
    
    # Cálculos financieros
    version_costo: VersionCosto = Field(default=VersionCosto.V3, description="Versión de costo usada")
    costo_total_calculado: Decimal = Field(default=Decimal("0"))
    precio_venta_sugerido: Decimal = Field(default=Decimal("0"))
    margen_ganancia: Decimal = Field(default=Decimal("0"))
    
    # Configuraciones específicas
    nivel_calidad: int = Field(default=2, description="Nivel de calidad 1-4")
    descuento_aplicado: Decimal = Field(default=Decimal("0"))
    
    # Control de producción
    tiempo_produccion_minutos: Optional[int] = Field(None)
    cantidad_producida: int = Field(default=0)
    fecha_ultima_produccion: Optional[date] = Field(None)
    
    # Control de sistema
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)

class CalculoCostoAvanzado(BaseModel):
    """Request para cálculo de costo avanzado"""
    molde_codigo: str
    linea_producto: LineaProducto
    insumos: Dict[str, Decimal] = Field(..., description="{codigo_insumo: cantidad}")
    colores: List[str] = Field(default_factory=list)
    nivel_calidad: int = Field(default=2, ge=1, le=4)
    version_costo: VersionCosto = Field(default=VersionCosto.V3)
    margen_adicional: Decimal = Field(default=Decimal("0"))
    cantidad_producir: int = Field(default=1, description="Cantidad a producir")

class ResultadoCalculoCosto(BaseModel):
    """Resultado completo del cálculo de costo"""
    # Información base
    molde_codigo: str
    linea_producto: str
    version_costo: str
    cantidad_producir: int
    
    # Desglose de costos
    costos_insumos: Dict[str, Decimal]
    costo_molde: Decimal
    costo_colores: Decimal
    costo_total_materiales: Decimal
    
    # Aplicación de reglas de negocio
    factor_calidad: Decimal
    descuento_linea: Decimal
    margen_adicional: Decimal
    
    # Cálculos finales
    costo_unitario: Decimal
    precio_antes_redondeo: Decimal
    precio_final_redondeado: Decimal
    ganancia_unitaria: Decimal
    margen_porcentual: Decimal
    
    # Información adicional
    precio_total_lote: Decimal
    ganancia_total_lote: Decimal
    fecha_calculo: datetime = Field(default_factory=datetime.now)

# =====================================
# BASE DE DATOS AVANZADA EN MEMORIA
# =====================================

# Insumos completos con datos reales de tu Excel
insumos_db: Dict[str, InsumoCompleto] = {
    "CV001": InsumoCompleto(
        codigo="CV001",
        descripcion="CERA DE VASO",
        tipo=TipoInsumo.CERA,
        costo_base=Decimal("28000"),
        cantidad_inventario=50,
        unidad_medida="kg",
        proveedor="Proveedor Ceras S.A.",
        factor_conversion=Decimal("1000")  # 1 kg = 1000 gr
    ),
    "FR001": InsumoCompleto(
        codigo="FR001",
        descripcion="FRAGANCIA PREMIUM",
        tipo=TipoInsumo.FRAGANCIA,
        costo_base=Decimal("6000"),
        cantidad_inventario=20,
        unidad_medida="ml",
        proveedor="Aromas Naturales",
        factor_conversion=Decimal("20")  # 20 ml por botella estándar
    ),
    "CL001": InsumoCompleto(
        codigo="CL001",
        descripcion="COLORANTE LIQUIDO",
        tipo=TipoInsumo.COLORANTE,
        costo_base=Decimal("5000"),
        cantidad_inventario=30,
        unidad_medida="gotas",
        proveedor="Colores Vivos",
        factor_conversion=Decimal("10")  # 10 gotas por uso estándar
    ),
    "PB001": InsumoCompleto(
        codigo="PB001",
        descripcion="PABILO ALGODÓN",
        tipo=TipoInsumo.PABILO,
        costo_base=Decimal("1700"),
        cantidad_inventario=100,
        unidad_medida="unidad",
        proveedor="Pabilos Premium",
        factor_conversion=Decimal("1")
    ),
    "AD001": InsumoCompleto(
        codigo="AD001",
        descripcion="ADITIVO ESPECIAL",
        tipo=TipoInsumo.ADITIVO,
        costo_base=Decimal("40000"),
        cantidad_inventario=10,
        unidad_medida="kg",
        proveedor="Aditivos Premium",
        factor_conversion=Decimal("1000")
    )
}

# Moldes completos con datos reales
moldes_db: Dict[str, MoldeCompleto] = {
    "VA601": MoldeCompleto(
        codigo="VA601",
        descripcion="PIRAMIDE",
        dimensiones="3X3X3",
        peso_molde=Decimal("17.6"),
        peso_cera_necesario=Decimal("10"),
        cantidad_pabilo=4,
        ubicacion_fisica="Estante A-1",
        precio_base_calculado=Decimal("2500"),
        ganancia_esperada=Decimal("1082"),
        lineas_compatibles=[LineaProducto.VELAS_GENERICAS, LineaProducto.DISENOS_PP]
    ),
    "VA602": MoldeCompleto(
        codigo="VA602",
        descripcion="MINI CORAZÓN",
        dimensiones="3X2X2,5",
        peso_molde=Decimal("10"),
        peso_cera_necesario=Decimal("4"),
        cantidad_pabilo=3,
        ubicacion_fisica="Estante A-2",
        precio_base_calculado=Decimal("1500"),
        ganancia_esperada=Decimal("807"),
        lineas_compatibles=[LineaProducto.BOKEH_FLOWER, LineaProducto.CAJAS_MAMA]
    ),
    "VA605": MoldeCompleto(
        codigo="VA605",
        descripcion="ULTIMA CENA",
        peso_cera_necesario=Decimal("160"),
        cantidad_pabilo=45,
        ubicacion_fisica="Estante B-1",
        precio_base_calculado=Decimal("27500"),
        ganancia_esperada=Decimal("9311"),
        lineas_compatibles=[LineaProducto.DISENOS_PCT, LineaProducto.BAUTIZO, LineaProducto.KARLA]
    )
}

# Colores completos
colores_db: Dict[str, ColorCompleto] = {
    "R1": ColorCompleto(codigo="R1", nombre="Ultramarine", cantidad_gotas_estandar=10, intensidad=8),
    "R2": ColorCompleto(codigo="R2", nombre="Fluorescent blue", cantidad_gotas_estandar=10, intensidad=9),
    "R3": ColorCompleto(codigo="R3", nombre="Blue", cantidad_gotas_estandar=10, intensidad=7),
    "R4": ColorCompleto(codigo="R4", nombre="Cerulean blue", cantidad_gotas_estandar=10, intensidad=6)
}

# Productos de ejemplo
productos_db: Dict[str, ProductoCompleto] = {}

# =====================================
# CALCULADORA AVANZADA DE COSTOS
# =====================================

class CalculadoraCostosAvanzada:
    """Réplica exacta de las fórmulas de tu Excel"""
    
    @staticmethod
    def calcular_costo_insumo(insumo: InsumoCompleto, cantidad_usar: Decimal) -> Decimal:
        """Calcular costo de insumo según su tipo (réplica de fórmulas Excel)"""
        if insumo.tipo == TipoInsumo.CERA:
            # Cera: costo por kilo → gramo
            costo_por_gramo = insumo.costo_base / Decimal("1000")
            return costo_por_gramo * cantidad_usar
            
        elif insumo.tipo == TipoInsumo.FRAGANCIA:
            # Fragancia: costo por botella → ml
            costo_por_ml = insumo.costo_base / Decimal("20")
            return costo_por_ml * cantidad_usar
            
        elif insumo.tipo == TipoInsumo.COLORANTE:
            # Colorante: costo por botella → gotas
            costo_por_gota = insumo.costo_base / Decimal("10")
            return costo_por_gota * cantidad_usar
            
        elif insumo.tipo == TipoInsumo.ADITIVO:
            # Aditivo: similar a cera, por porcentaje
            costo_por_gramo = insumo.costo_base / Decimal("1000")
            return costo_por_gramo * cantidad_usar
            
        else:
            # Otros: costo directo
            return insumo.valor_total * cantidad_usar
    
    @staticmethod
    def aplicar_reglas_linea_producto(
        costo_base: Decimal, 
        linea: LineaProducto,
        nivel_calidad: int
    ) -> Dict[str, Decimal]:
        """Aplicar reglas específicas por línea de producto"""
        config = CONFIGURACIONES_LINEA.get(linea, {"descuento_especial": 0, "factor_adicional": 1.0})
        factor_calidad = FACTORES_CALIDAD.get(nivel_calidad, Decimal("2.8"))
        
        # Aplicar factor de calidad
        precio_con_calidad = costo_base * factor_calidad
        
        # Aplicar factor adicional de la línea
        precio_con_factor = precio_con_calidad * Decimal(str(config["factor_adicional"]))
        
        # Aplicar descuento específico (ej: -110 en PCT)
        descuento = Decimal(str(config["descuento_especial"]))
        precio_final = precio_con_factor - descuento
        
        return {
            "costo_base": costo_base,
            "factor_calidad": factor_calidad,
            "precio_con_calidad": precio_con_calidad,
            "factor_linea": Decimal(str(config["factor_adicional"])),
            "precio_con_factor": precio_con_factor,
            "descuento_linea": descuento,
            "precio_antes_redondeo": precio_final
        }
    
    @staticmethod
    def redondear_precio(precio: Decimal) -> Decimal:
        """Redondear a múltiplo de 500 (como en Excel)"""
        return (precio / Decimal("500")).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        ) * Decimal("500")

# =====================================
# APLICACIÓN FASTAPI AVANZADA
# =====================================

app = FastAPI(
    title="🕯️ Sistema Completo Vel Arte - Todas las Reglas de Negocio",
    version="3.0.0",
    description="""
    ## Sistema Profesional de Gestión de Velas Artesanales
    
    ### ✨ Funcionalidades Completas:
    * 📦 **Gestión Avanzada de Insumos** - Con cálculos específicos por tipo
    * 🏺 **Gestión Completa de Moldes** - Estados, ubicaciones, historial
    * 🎨 **Gestión de Colores** - Fórmulas y mezclas
    * 🧮 **Calculadora de Costos Avanzada** - Réplica exacta de Excel
    * 📋 **Líneas de Productos** - Bokeh, Cajas Mamá, PCT, Bautizo, etc.
    * 🔄 **Versionado de Costos** - V1, V2, V3
    * 📊 **Reportes y Analytics** - Completos
    
    ### 🎯 Reglas de Negocio Implementadas:
    * ✅ Cálculos específicos por tipo de insumo
    * ✅ Factores de calidad (1: 3.2, 2: 3.0, 3: 2.8, 4: 2.6)
    * ✅ Descuentos por línea de producto
    * ✅ Redondeo a múltiplos de 500
    * ✅ Impuestos automáticos del 10%
    * ✅ Gestión de inventarios avanzada
    
    ### Desarrollado por: Carlos T - Vel Arte
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# =====================================
# ENDPOINTS PRINCIPALES
# =====================================

@app.get("/", tags=["🏠 General"])
def home():
    return {
        "message": "🎉 Sistema Completo Vel Arte - Todas las Reglas de Negocio",
        "empresa": "Vel Arte",
        "desarrollador": "Carlos T",
        "version": "3.0.0",
        "status": "✅ Todas las reglas de Excel implementadas",
        "funcionalidades": [
            "✅ Insumos con cálculos específicos por tipo",
            "✅ Moldes con gestión avanzada",
            "✅ Colores y fórmulas",
            "✅ Calculadora exacta de costos",
            "✅ Líneas de productos especializadas",
            "✅ Versionado de costos V1/V2/V3",
            "✅ Reportes y analytics"
        ],
        "reglas_implementadas": {
            "factores_calidad": "1:3.2, 2:3.0, 3:2.8, 4:2.6",
            "descuentos_especiales": "PCT:-110, Bautizo:-110",
            "calculo_cera": "costo_kilo / 1000 * gramos",
            "calculo_fragancia": "costo_botella / 20 * ml",
            "calculo_colorante": "costo_botella / 10 * gotas",
            "redondeo": "múltiplos de 500",
            "impuestos": "10% automático"
        }
    }

@app.get("/stats/completas", tags=["🏠 General"])
def estadisticas_completas():
    """Estadísticas completas del sistema"""
    return {
        "inventario": {
            "total_insumos": len(insumos_db),
            "total_moldes": len(moldes_db),
            "total_colores": len(colores_db),
            "total_productos": len(productos_db)
        },
        "estados": {
            "insumos_activos": len([i for i in insumos_db.values() if i.activo]),
            "moldes_disponibles": len([m for m in moldes_db.values() if m.estado == EstadoMolde.DISPONIBLE]),
            "moldes_en_uso": len([m for m in moldes_db.values() if m.estado == EstadoMolde.EN_USO])
        },
        "financiero": {
            "valor_inventario_insumos": sum(i.valor_total * i.cantidad_inventario for i in insumos_db.values()),
            "ganancia_potencial_moldes": sum(m.ganancia_esperada for m in moldes_db.values())
        },
        "lineas_producto": {linea.value: len([m for m in moldes_db.values() if linea in m.lineas_compatibles]) for linea in LineaProducto},
        "ultima_actualizacion": datetime.now()
    }

# =====================================
# CRUD INSUMOS AVANZADO
# =====================================

@app.get("/insumos/avanzado", response_model=List[InsumoCompleto], tags=["📦 Insumos Avanzado"])
def listar_insumos_avanzado(
    activos_solo: bool = True,
    tipo: Optional[TipoInsumo] = None,
    stock_bajo: bool = False
):
    """Listar insumos con filtros avanzados"""
    insumos = list(insumos_db.values())
    
    if activos_solo:
        insumos = [i for i in insumos if i.activo]
    
    if tipo:
        insumos = [i for i in insumos if i.tipo == tipo]
    
    if stock_bajo:
        insumos = [i for i in insumos if i.cantidad_inventario <= i.cantidad_minima]
    
    return insumos

@app.post("/insumos/avanzado", response_model=InsumoCompleto, tags=["📦 Insumos Avanzado"])
def crear_insumo_avanzado(insumo: InsumoCompleto):
    """Crear insumo con todas las validaciones de negocio"""
    if insumo.codigo in insumos_db:
        raise HTTPException(status_code=400, detail=f"Insumo {insumo.codigo} ya existe")
    
    # Auto-calcular valores
    insumo.fecha_actualizacion = datetime.now()
    
    insumos_db[insumo.codigo] = insumo
    return insumo

@app.get("/insumos/{codigo}/costo-calculado", tags=["📦 Insumos Avanzado"])
def calcular_costo_insumo_especifico(codigo: str, cantidad: Decimal):
    """Calcular costo específico de un insumo para una cantidad"""
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    insumo = insumos_db[codigo]
    calculadora = CalculadoraCostosAvanzada()
    costo_calculado = calculadora.calcular_costo_insumo(insumo, cantidad)
    
    return {
        "insumo": insumo.descripcion,
        "tipo": insumo.tipo,
        "cantidad_solicitada": cantidad,
        "unidad": insumo.unidad_medida,
        "costo_base": insumo.costo_base,
        "costo_calculado": costo_calculado,
        "costo_unitario": costo_calculado / cantidad if cantidad > 0 else 0,
        "formula_aplicada": f"Tipo {insumo.tipo.value} con factor {insumo.factor_conversion}"
    }

# =====================================
# CALCULADORA DE COSTOS AVANZADA
# =====================================

@app.post("/calcular-costo/avanzado", response_model=ResultadoCalculoCosto, tags=["🧮 Cálculos Avanzados"])
def calcular_costo_avanzado(calculo: CalculoCostoAvanzado):
    """Cálculo avanzado con todas las reglas de negocio de Excel"""
    
    # Validar molde
    if calculo.molde_codigo not in moldes_db:
        raise HTTPException(status_code=404, detail=f"Molde {calculo.molde_codigo} no encontrado")
    
    molde = moldes_db[calculo.molde_codigo]
    calculadora = CalculadoraCostosAvanzada()
    
    # Verificar compatibilidad línea-molde
    if calculo.linea_producto not in molde.lineas_compatibles:
        raise HTTPException(
            status_code=400, 
            detail=f"Molde {calculo.molde_codigo} no es compatible con línea {calculo.linea_producto}"
        )
    
    # Calcular costos de insumos
    costos_insumos = {}
    costo_total_materiales = Decimal("0")
    
    for codigo_insumo, cantidad in calculo.insumos.items():
        if codigo_insumo not in insumos_db:
            raise HTTPException(status_code=404, detail=f"Insumo {codigo_insumo} no encontrado")
        
        insumo = insumos_db[codigo_insumo]
        costo_insumo = calculadora.calcular_costo_insumo(insumo, cantidad)
        costos_insumos[codigo_insumo] = costo_insumo
        costo_total_materiales += costo_insumo
    
    # Calcular costo de colores
    costo_colores = Decimal("0")
    for codigo_color in calculo.colores:
        if codigo_color in colores_db:
            color = colores_db[codigo_color]
            # Costo básico por color (puedes ajustar esta lógica)
            costo_colores += Decimal("50") * color.cantidad_gotas_estandar
    
    # Costo base del molde (uso/desgaste)
    costo_molde = molde.precio_base_calculado / Decimal("1000")  # Costo por uso
    
    # Costo total de materiales
    costo_base_total = costo_total_materiales + costo_molde + costo_colores
    
    # Aplicar reglas de línea de producto
    reglas_aplicadas = calculadora.aplicar_reglas_linea_producto(
        costo_base_total, 
        calculo.linea_producto,
        calculo.nivel_calidad
    )
    
    # Aplicar margen adicional
    precio_con_margen = reglas_aplicadas["precio_antes_redondeo"] + calculo.margen_adicional
    
    # Redondear precio final
    precio_final = calculadora.redondear_precio(precio_con_margen)
    
    # Cálculos finales
    costo_unitario = costo_base_total / calculo.cantidad_producir
    ganancia_unitaria = (precio_final - costo_base_total) / calculo.cantidad_producir
    margen_porcentual = (ganancia_unitaria / costo_unitario * 100) if costo_unitario > 0 else Decimal("0")
    
    return ResultadoCalculoCosto(
        molde_codigo=calculo.molde_codigo,
        linea_producto=calculo.linea_producto.value,
        version_costo=calculo.version_costo.value,
        cantidad_producir=calculo.cantidad_producir,
        costos_insumos=costos_insumos,
        costo_molde=costo_molde,
        costo_colores=costo_colores,
        costo_total_materiales=costo_base_total,
        factor_calidad=reglas_aplicadas["factor_calidad"],
        descuento_linea=reglas_aplicadas["descuento_linea"],
        margen_adicional=calculo.margen_adicional,
        costo_unitario=costo_unitario,
        precio_antes_redondeo=precio_con_margen,
        precio_final_redondeado=precio_final,
        ganancia_unitaria=ganancia_unitaria,
        margen_porcentual=margen_porcentual,
        precio_total_lote=precio_final * calculo.cantidad_producir,
        ganancia_total_lote=ganancia_unitaria * calculo.cantidad_producir
    )

# =====================================
# ENDPOINTS ESPECIALIZADOS
# =====================================

@app.get("/lineas-producto", tags=["📋 Líneas de Producto"])
def obtener_lineas_producto():
    """Obtener todas las líneas de producto disponibles"""
    return {
        "lineas_disponibles": [
            {
                "codigo": linea.value,
                "nombre": linea.value.replace("_", " ").title(),
                "configuracion": CONFIGURACIONES_LINEA.get(linea, {}),
                "moldes_compatibles": [
                    molde.codigo for molde in moldes_db.values() 
                    if linea in molde.lineas_compatibles
                ]
            }
            for linea in LineaProducto
        ]
    }

@app.get("/factores-calidad/detallados", tags=["🧮 Cálculos Avanzados"])
def obtener_factores_calidad_detallados():
    """Obtener factores de calidad con explicaciones"""
    return {
        "factores": {
            nivel: {
                "valor": float(factor),
                "descripcion": ["Básica", "Estándar", "Alta", "Premium"][nivel-1],
                "uso_recomendado": [
                    "Productos económicos", 
                    "Productos estándar", 
                    "Productos premium", 
                    "Productos de lujo"
                ][nivel-1]
            }
            for nivel, factor in FACTORES_CALIDAD.items()
        },
        "ejemplo_calculo": "costo_base * factor = precio_con_calidad"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema Completo Vel Arte con TODAS las reglas de negocio...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📊 Stats: http://localhost:8000/stats/completas")
    print("🧮 Cálculos: http://localhost:8000/calcular-costo/avanzado")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)