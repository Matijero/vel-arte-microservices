#!/bin/bash
echo "🧹 LIMPIEZA RÁPIDA"
echo "=================="

# 1. Eliminar archivos basura
rm -f diagnose_*.sh audit_*.sh fix_*.sh test_*.sh
rm -f */Dockerfile.temp */Dockerfile.bak */.env.clean

# 2. Verificar .gitignore
if [ ! -f ".gitignore" ]; then
    echo "Creando .gitignore..."
    cat > .gitignore << 'EOF'
.env
*.env
__pycache__/
venv/
*.log
.vscode/
.idea/
EOF
fi

echo "✅ Limpieza completada"