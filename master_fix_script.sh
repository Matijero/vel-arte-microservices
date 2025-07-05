#!/bin/bash
# 🔧 SCRIPT MAESTRO PARA RESOLVER TODOS LOS PROBLEMAS

echo "🔧 RESOLVIENDO TODOS LOS PROBLEMAS DEL PROYECTO"
echo "=============================================="
echo "⏰ $(date)"
echo ""

# VERIFICAR QUE ESTAMOS EN EL DIRECTORIO CORRECTO
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ ERROR: No estás en el directorio del proyecto"
    echo "   Ejecuta: cd '/d/Proyecto Vel Arte/vel-arte-microservices'"
    exit 1
fi

# FIX 1: LIMPIAR ARCHIVOS TEMPORALES
echo "🧹 FIX 1: LIMPIANDO ARCHIVOS TEMPORALES"
echo "======================================="
# Eliminar archivos de diagnóstico temporales
rm -f diagnose_*.sh audit_*.sh fix_*.sh test_*.sh final_*.sh start_*.sh
rm -f */Dockerfile.temp */Dockerfile.fixed */Dockerfile.bak */.env.clean
rm -f */src/core/config_fixed.py
echo "✅ Archivos temporales eliminados"

# FIX 2: ARREGLAR WARNING DE DOCKER-COMPOSE
echo ""
echo "🐳 FIX 2: ARREGLANDO DOCKER-COMPOSE WARNING"
echo "==========================================="
# El warning "variable 'a' not set" puede venir de un typo en docker-compose.yml
# Verificar si existe
if grep -q '\${a}' docker-compose.yml 2>/dev/null; then
    cp docker-compose.yml docker-compose.yml.bak
    sed -i 's/\${a}//g' docker-compose.yml
    echo "✅ Variable 'a' corregida en docker-compose.yml"
else
    echo "✅ No se encontró el problema de variable 'a'"
fi

# FIX 3: ASEGURAR QUE .GITIGNORE ESTÁ CORRECTO
echo ""
echo "📝 FIX 3: VERIFICANDO .GITIGNORE"
echo "================================"
if [ ! -f ".gitignore" ]; then
    echo "❌ No existe .gitignore - CREÁNDOLO"
    cat > .gitignore << 'EOF'
# Environment files
.env
*.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
*.pid

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# Frontend
node_modules/
build/
dist/
EOF
    echo "✅ .gitignore creado"
else
    echo "✅ .gitignore existe"
fi

# FIX 4: CREAR DOCUMENTACIÓN ESENCIAL
echo ""
echo "📚 FIX 4: CREANDO DOCUMENTACIÓN ESENCIAL"
echo "========================================"

# README.md mejorado
cat > README.md << 'EOF'
# Vel Arte Microservices

Sistema de gestión empresarial para Vel Arte basado en arquitectura de microservicios.

## 🚀 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/Matijero/vel-arte-microservices.git
cd vel-arte-microservices

# 2. Generar archivos .env seguros
python generate_secrets.py

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar estado
curl http://localhost:8000/health