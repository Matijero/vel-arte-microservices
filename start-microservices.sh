#!/bin/bash

echo "🚀 Iniciando Vel Arte Microservices..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker y Docker Compose encontrados"

# Construir y levantar servicios
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.microservices.yml build

echo "🚀 Levantando servicios..."
docker-compose -f docker-compose.microservices.yml up -d

echo "⏳ Esperando que los servicios inicien..."
sleep 30

# Verificar servicios
echo "🔍 Verificando estado de servicios..."

services=("auth-service:8001" "product-service:8002" "inventory-service:8003" "pricing-service:8004" "api-gateway:8000")

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    if curl -s -f http://localhost:$port/health > /dev/null; then
        echo "✅ $name: OK"
    else
        echo "❌ $name: FAIL"
    fi
done

echo ""
echo "🎉 Microservicios iniciados!"
echo ""
echo "📊 URLs disponibles:"
echo "  • API Gateway:     http://localhost:8000"
echo "  • Auth Service:    http://localhost:8001"  
echo "  • Product Service: http://localhost:8002"
echo "  • Inventory:       http://localhost:8003"
echo "  • Pricing:         http://localhost:8004"
echo "  • MongoDB UI:      http://localhost:8081"
echo ""
echo "🔧 Comandos útiles:"
echo "  • Ver logs:        docker-compose -f docker-compose.microservices.yml logs -f"
echo "  • Parar todo:      docker-compose -f docker-compose.microservices.yml down"
echo "  • Reiniciar:       docker-compose -f docker-compose.microservices.yml restart"
