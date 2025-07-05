#!/bin/bash
echo "=== DIAGNÓSTICO DE ARCHIVOS ==="
echo ""
echo "1. AUTH SERVICE:"
echo "- Requirements tiene JWT?: "
grep -c "JWT" services/auth-service/requirements.txt || echo "NO"
echo "- Estructura de directorios:"
find services/auth-service/src -type f -name "*.py" | sort
echo ""
echo "2. PRODUCT SERVICE:"
echo "- Requirements tiene JWT?: "
grep -c "JWT" services/product-service/requirements.txt || echo "NO"
echo "- Routes.py importaciones:"
grep "from" services/product-service/src/api/routes.py | grep -E "(import|from)" | head -5
echo "- Auth.py existe?: "
ls -la services/product-service/src/utils/auth.py 2>/dev/null || echo "NO EXISTE"
echo ""
echo "3. DOCKER STATUS:"
docker ps -a --filter "name=vel_arte" --format "table {{.Names}}\t{{.Status}}"
