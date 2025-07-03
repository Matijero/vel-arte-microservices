import pandas as pd
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import re
import math

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigradorExcel:
    """Migra todos los datos del Excel a MongoDB"""
    
    def __init__(self, archivo_excel: str, database_url: str = "mongodb://localhost:27017/"):
        self.archivo_excel = archivo_excel
        self.database_url = database_url
        self.client = None
        self.db = None
        
    async def conectar_db(self):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.database_url)
            self.db = self.client.velas_db
            await self.client.admin.command('ping')
            logger.info("✅ Conectado a MongoDB para migración")
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    async def cerrar_db(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            logger.info("🔒 Conexión cerrada")
    
    def limpiar_valor_monetario(self, valor):
        """Limpiar valores monetarios de Excel"""
        if pd.isna(valor) or valor == "":
            return 0.0
        
        if isinstance(valor, (int, float)):
            return float(valor)
        
        # Limpiar string monetario
        if isinstance(valor, str):
            # Remover $, espacios, comas
            valor_limpio = re.sub(r'[\$\s,]', '', str(valor))
            try:
                return float(valor_limpio)
            except:
                return 0.0
        
        return 0.0
    
    def determinar_tipo_insumo(self, codigo: str, descripcion: str) -> str:
        """Determinar tipo de insumo basado en código y descripción"""
        codigo = str(codigo).upper()
        descripcion = str(descripcion).upper()
        
        if codigo.startswith('CV') or 'CERA' in descripcion:
            return "cera"
        elif codigo.startswith('FR') or 'FRAGANCIA' in descripcion:
            return "fragancia"
        elif codigo.startswith('CL') or 'COLOR' in descripcion:
            return "colorante"
        elif codigo.startswith('PB') or 'PABILO' in descripcion:
            return "pabilo"
        elif codigo.startswith('AD') or 'ADITIVO' in descripcion:
            return "aditivo"
        elif 'ENVASE' in descripcion or 'VIDRIO' in descripcion:
            return "envase"
        else:
            return "otros"
    
    async def migrar_insumos(self):
        """Migrar datos de la hoja Insumos"""
        logger.info("📦 Iniciando migración de insumos...")
        
        try:
            # Leer hoja de insumos
            df_insumos = pd.read_excel(self.archivo_excel, sheet_name='Insumos')
            logger.info(f"📄 Leyendo {len(df_insumos)} filas de insumos")
            
            insumos_migrados = 0
            errores = 0
            
            for index, row in df_insumos.iterrows():
                try:
                    # Saltar filas vacías
                    if pd.isna(row.get('CODIGO', '')) or row.get('CODIGO', '') == '':
                        continue
                    
                    codigo = str(row['CODIGO']).strip()
                    descripcion = str(row.get('DESCRIPCION', '')).strip()
                    
                    if codigo == '' or descripcion == '':
                        continue
                    
                    # Preparar datos del insumo
                    insumo_data = {
                        'codigo': codigo,
                        'descripcion': descripcion,
                        'capacidad': str(row.get('CAPACIDAD', '')).strip() if not pd.isna(row.get('CAPACIDAD')) else None,
                        'tipo': self.determinar_tipo_insumo(codigo, descripcion),
                        'costo_base': self.limpiar_valor_monetario(row.get('COSTO', 0)),
                        'impuesto': self.limpiar_valor_monetario(row.get('IMPUESTO', 0)),
                        'cantidad_inventario': int(row.get('CANTIDAD', 0)) if not pd.isna(row.get('CANTIDAD')) else 0,
                        'costo_envio': self.limpiar_valor_monetario(row.get('ENVIO', 0)),
                        'valor_total': self.limpiar_valor_monetario(row.get('VALOR TOTAL', 0)),
                        'proveedor': str(row.get('PROVEEDOR', '')).strip() if not pd.isna(row.get('PROVEEDOR')) else None,
                        'unidad_medida': 'unidad',  # Determinar automáticamente después
                        'activo': True,
                        'fecha_creacion': datetime.now(),
                        'fecha_actualizacion': datetime.now()
                    }
                    
                    # Determinar unidad de medida
                    if insumo_data['tipo'] == 'cera':
                        insumo_data['unidad_medida'] = 'kg'
                    elif insumo_data['tipo'] == 'fragancia':
                        insumo_data['unidad_medida'] = 'ml'
                    elif insumo_data['tipo'] == 'colorante':
                        insumo_data['unidad_medida'] = 'ml'
                    elif insumo_data['tipo'] == 'pabilo':
                        insumo_data['unidad_medida'] = 'unidad'
                    
                    # Insertar en MongoDB (actualizar si existe)
                    await self.db.insumos.update_one(
                        {'codigo': codigo},
                        {'$set': insumo_data},
                        upsert=True
                    )
                    
                    insumos_migrados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando insumo {index}: {e}")
                    errores += 1
            
            logger.info(f"✅ Migración de insumos completada: {insumos_migrados} migrados, {errores} errores")
            return {"migrados": insumos_migrados, "errores": errores}
            
        except Exception as e:
            logger.error(f"❌ Error en migración de insumos: {e}")
            raise
    
    async def migrar_moldes(self):
        """Migrar datos de la hoja Moldes"""
        logger.info("🏺 Iniciando migración de moldes...")
        
        try:
            df_moldes = pd.read_excel(self.archivo_excel, sheet_name='Moldes')
            logger.info(f"📄 Leyendo {len(df_moldes)} filas de moldes")
            
            moldes_migrados = 0
            errores = 0
            
            for index, row in df_moldes.iterrows():
                try:
                    if pd.isna(row.get('CÓDIGO DEL MOLDE', '')) or row.get('CÓDIGO DEL MOLDE', '') == '':
                        continue
                    
                    codigo = str(row['CÓDIGO DEL MOLDE']).strip()
                    descripcion = str(row.get('DESCRIPCIÓN', '')).strip()
                    
                    if codigo == '' or descripcion == '':
                        continue
                    
                    molde_data = {
                        'codigo': codigo,
                        'descripcion': descripcion,
                        'tipo_vela': str(row.get('TIPO DE VELA', '')).strip() if not pd.isna(row.get('TIPO DE VELA')) else None,
                        'material_molde': str(row.get('MATERIAL', '')).strip() if not pd.isna(row.get('MATERIAL')) else None,
                        'dimensiones': str(row.get('TAMAÑO', '')).strip() if not pd.isna(row.get('TAMAÑO')) else None,
                        'peso_molde': float(row.get('PESO MOLDE', 0)) if not pd.isna(row.get('PESO MOLDE')) else None,
                        'peso_cera_necesario': float(row.get('PESO DE CERA', 0)) if not pd.isna(row.get('PESO DE CERA')) else 0,
                        'cantidad_pabilo': int(row.get('PABILO', 0)) if not pd.isna(row.get('PABILO')) else 0,
                        'estado': 'disponible',
                        'ubicacion_fisica': str(row.get('UBICACIÓN', '')).strip() if not pd.isna(row.get('UBICACIÓN')) else None,
                        'precio_base_calculado': self.limpiar_valor_monetario(row.get('VALOR', 0)),
                        'ganancia_esperada': self.limpiar_valor_monetario(row.get('GANANCIA', 0)),
                        'lineas_compatibles': ['velas_genericas'],  # Determinar después
                        'activo': True,
                        'fecha_creacion': datetime.now(),
                        'fecha_actualizacion': datetime.now()
                    }
                    
                    await self.db.moldes.update_one(
                        {'codigo': codigo},
                        {'$set': molde_data},
                        upsert=True
                    )
                    
                    moldes_migrados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando molde {index}: {e}")
                    errores += 1
            
            logger.info(f"✅ Migración de moldes completada: {moldes_migrados} migrados, {errores} errores")
            return {"migrados": moldes_migrados, "errores": errores}
            
        except Exception as e:
            logger.error(f"❌ Error en migración de moldes: {e}")
            raise
    
    async def migrar_colores(self):
        """Migrar datos de la hoja Color"""
        logger.info("🎨 Iniciando migración de colores...")
        
        try:
            df_colores = pd.read_excel(self.archivo_excel, sheet_name='Color')
            logger.info(f"📄 Leyendo {len(df_colores)} filas de colores")
            
            colores_migrados = 0
            errores = 0
            
            for index, row in df_colores.iterrows():
                try:
                    if pd.isna(row.get('CÓDIGO COLOR', '')) or row.get('CÓDIGO COLOR', '') == '':
                        continue
                    
                    codigo = str(row['CÓDIGO COLOR']).strip()
                    nombre = str(row.get('NOMBRE COLOR', '')).strip()
                    
                    if codigo == '' or nombre == '':
                        continue
                    
                    color_data = {
                        'codigo': codigo,
                        'nombre': nombre,
                        'cantidad_gotas_estandar': int(row.get('CANTIDAD GOTAS', 10)) if not pd.isna(row.get('CANTIDAD GOTAS')) else 10,
                        'intensidad': 5,  # Valor por defecto
                        'tipo_base': 'liquido',
                        'stock_actual': 100,  # Valor inicial
                        'activo': True,
                        'fecha_creacion': datetime.now(),
                        'fecha_actualizacion': datetime.now()
                    }
                    
                    await self.db.colores.update_one(
                        {'codigo': codigo},
                        {'$set': color_data},
                        upsert=True
                    )
                    
                    colores_migrados += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando color {index}: {e}")
                    errores += 1
            
            logger.info(f"✅ Migración de colores completada: {colores_migrados} migrados, {errores} errores")
            return {"migrados": colores_migrados, "errores": errores}
            
        except Exception as e:
            logger.error(f"❌ Error en migración de colores: {e}")
            raise
    
    async def ejecutar_migracion_completa(self):
        """Ejecutar migración completa"""
        logger.info("🚀 Iniciando migración completa de Excel a MongoDB")
        
        resultados = {
            'inicio': datetime.now(),
            'insumos': None,
            'moldes': None, 
            'colores': None,
            'errores_generales': []
        }
        
        try:
            await self.conectar_db()
            
            # Migrar insumos
            resultados['insumos'] = await self.migrar_insumos()
            
            # Migrar moldes
            resultados['moldes'] = await self.migrar_moldes()
            
            # Migrar colores
            resultados['colores'] = await self.migrar_colores()
            
            resultados['fin'] = datetime.now()
            resultados['duracion'] = str(resultados['fin'] - resultados['inicio'])
            
            logger.info("🎉 ¡MIGRACIÓN COMPLETA EXITOSA!")
            
        except Exception as e:
            logger.error(f"❌ Error en migración: {e}")
            resultados['errores_generales'].append(str(e))
        
        finally:
            await self.cerrar_db()
        
        return resultados

# Función principal para ejecutar
async def main():
    """Función principal de migración"""
    migrador = MigradorExcel('costos velas.xlsx')
    resultados = await migrador.ejecutar_migracion_completa()
    
    print("\n" + "="*60)
    print("📊 RESULTADOS DE LA MIGRACIÓN")
    print("="*60)
    print(f"⏱️  Duración: {resultados.get('duracion', 'N/A')}")
    print(f"📦 Insumos: {resultados['insumos']['migrados'] if resultados['insumos'] else 0} migrados")
    print(f"🏺 Moldes: {resultados['moldes']['migrados'] if resultados['moldes'] else 0} migrados")
    print(f"🎨 Colores: {resultados['colores']['migrados'] if resultados['colores'] else 0} migrados")
    
    if resultados['errores_generales']:
        print(f"❌ Errores generales: {len(resultados['errores_generales'])}")
    else:
        print("✅ Sin errores generales")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
