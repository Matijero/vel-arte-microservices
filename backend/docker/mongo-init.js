// Inicialización de la base de datos
db = db.getSiblingDB('velas_db');

// Crear usuario para la aplicación
db.createUser({
    user: 'velas_app',
    pwd: 'velas_password',
    roles: [
        {
            role: 'readWrite',
            db: 'velas_db'
        }
    ]
});

// Crear colecciones iniciales basadas en tu Excel
db.createCollection('insumos');
db.createCollection('moldes');
db.createCollection('colores');
db.createCollection('productos');
db.createCollection('cotizaciones');
db.createCollection('usuarios');
db.createCollection('versiones_costos');

// Crear índices para mejor rendimiento
db.insumos.createIndex({ "codigo": 1 }, { unique: true });
db.moldes.createIndex({ "codigo": 1 }, { unique: true });
db.colores.createIndex({ "codigo": 1 }, { unique: true });
db.productos.createIndex({ "codigo": 1 }, { unique: true });

print('✅ Base de datos inicializada correctamente');
print('📦 Colecciones creadas: insumos, moldes, colores, productos, cotizaciones, usuarios');
print('🔍 Índices creados para optimizar búsquedas');
