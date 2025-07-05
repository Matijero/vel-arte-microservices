#!/bin/bash
echo "🚀 REINICIANDO SISTEMA VEL ARTE COMPLETO..."
echo "========================================"

# Limpiar estado previo
echo "🧹 Limpiando estado previo..."
docker-compose down --remove-orphans 2>/dev/null || true
docker container prune -f 2>/dev/null || true

# Verificar herramientas
echo "🔧 Verificando herramientas..."
echo "Docker version:"
docker --version
echo "Docker Compose version:"
docker-compose --version
echo "Node version:"
node --version
echo "NPM version:"
npm --version

# Arrancar backend
echo ""
echo "🐳 Iniciando backend..."
docker-compose up -d --build

# Esperar servicios
echo "⏳ Esperando que servicios estén listos..."
for i in {1..30}; do
    if curl -sf "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "✅ Backend listo!"
        break
    fi
    echo "   Intento $i/30..."
    sleep 2
done

# Verificar endpoints
echo ""
echo "🧪 Verificando endpoints:"
for endpoint in health insumos moldes colores resumen-completo; do
    echo -n "  /$endpoint: "
    if curl -sf "http://localhost:8000/$endpoint" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAIL"
    fi
done

# Estado final
echo ""
echo "📊 Estado de contenedores:"
docker-compose ps

echo ""
echo "🎯 BACKEND COMPLETADO"
echo "===================="
echo "✅ API disponible en: http://localhost:8000"
echo "📚 Documentación en: http://localhost:8000/docs"
echo ""
echo "🚀 SIGUIENTE PASO: Arrancar frontend"
echo "   Abre NUEVA terminal Git Bash"
echo "   Ejecuta: cd '/d/Proyecto Vel Arte/vel-arte-microservices/frontend'"
echo "   Luego: npm install && npm start"
echo ""
echo "⏳ Mantén esta terminal abierta (backend ejecutándose)"