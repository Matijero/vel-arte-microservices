# TODO - Vel Arte Microservices

## 🚨 CRÍTICO - Seguridad
- [ ] Agregar .gitignore con:
  ```
  .env
  *.env
  .env.*
  venv/
  __pycache__/
  *.pyc
  .pytest_cache/
  ```
- [ ] Remover archivos .env del repositorio
- [ ] Crear .env.example para cada servicio
- [ ] Agregar USER en Dockerfiles
- [ ] Implementar rate limiting
- [ ] Configurar HTTPS/TLS

## 🏗️ Arquitectura
- [ ] Reestructurar auth-service:
  - [ ] Crear carpeta domain/
  - [ ] Crear carpeta use_cases/
  - [ ] Crear carpeta infrastructure/
  - [ ] Implementar Repository Pattern
- [ ] Reestructurar product-service (igual que auth)
- [ ] Mejorar api-gateway structure

## ⚙️ Funcionalidad
- [ ] Implementar CRUD configuraciones
- [ ] Implementar gestión productos
- [ ] Motor de cálculos real
- [ ] Sistema de cotizaciones
- [ ] Generación de reportes

## 🧪 Testing
- [ ] Configurar pytest
- [ ] Tests unitarios auth-service
- [ ] Tests unitarios product-service
- [ ] Tests unitarios business-rules
- [ ] Tests de integración

## 📚 Documentación
- [ ] README.md por servicio
- [ ] API.md con ejemplos
- [ ] ARCHITECTURE.md
- [ ] DEPLOYMENT.md
- [ ] CONTRIBUTING.md
