#!/bin/bash
# 🎯 FIXES CRÍTICOS PARA VERSIÓN FUNCIONAL EN GITHUB

echo "🎯 PREPARANDO VERSIÓN FUNCIONAL PARA GITHUB"
echo "==========================================="
echo "⏰ $(date)"
echo ""

# PRIORIDAD 1: LIMPIAR ARCHIVOS SENSIBLES Y TEMPORALES
echo "🔴 PRIORIDAD 1: LIMPIEZA CRÍTICA"
echo "================================="

# Verificar que .gitignore esté correcto
if [ ! -f .gitignore ]; then
    echo "❌ CRÍTICO: No hay .gitignore!"
    exit 1
fi

# Eliminar archivos temporales de fixes
rm -f */Dockerfile.temp */Dockerfile.fixed */Dockerfile.bak */.env.clean
rm -f diagnose_*.sh audit_*.sh fix_*.sh test_*.sh
echo "✅ Archivos temporales eliminados"

# PRIORIDAD 2: VERIFICAR SERVICIOS FUNCIONANDO
echo ""
echo "🟡 PRIORIDAD 2: VERIFICACIÓN DE SERVICIOS"
echo "========================================="

services=("8000:gateway" "8001:auth" "8002:products" "8003:business-rules")
all_working=true

for service in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service"
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ $name está funcionando"
    else
        echo "❌ $name NO responde"
        all_working=false
    fi
done

if [ "$all_working" = false ]; then
    echo "⚠️  Algunos servicios no responden. Ejecutar: docker-compose up -d"
fi

# PRIORIDAD 3: DOCUMENTACIÓN MÍNIMA
echo ""
echo "🟢 PRIORIDAD 3: DOCUMENTACIÓN ESENCIAL"
echo "======================================"

# README.md principal
if [ ! -f README.md ]; then
cat > README.md << 'EOF'
# Vel Arte Microservices

Sistema de gestión para Vel Arte basado en microservicios.

## 🚀 Quick Start

```bash
# 1. Clonar repositorio
git clone [tu-repo-url]
cd vel-arte-microservices

# 2. Configurar variables de entorno
cp auth-service/.env.example auth-service/.env
cp product-service/.env.example product-service/.env
cp business-rules-service/.env.example business-rules-service/.env
cp api-gateway/.env.example api-gateway/.env

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/health