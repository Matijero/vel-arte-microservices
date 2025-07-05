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
