#!/bin/bash
# 🎯 Verificación Final - Servicios Healthy

echo "🎯 VERIFICACIÓN FINAL DEL SISTEMA"
echo "================================="
echo "⏰ $(date)"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# PASO 1: VERIFICAR ESTADO DE CONTENEDORES
echo "🐳 PASO 1: ESTADO DE CONTENEDORES DOCKER"
echo "========================================"

log_info "Estado actual de contenedores:"
docker-compose ps

echo ""
log_info "Verificando contenedores healthy..."

# Verificar que todos estén healthy
healthy_count=$(docker-compose ps | grep "healthy" | wc -l)
total_services=5  # mongodb, auth, product, business-rules, gateway

echo "📊 Contenedores healthy: $healthy_count/$total_services"

if [ $healthy_count -eq $total_services ]; then
    log_success "Todos los contenedores están healthy"
else
    log_warning "Algunos contenedores no están healthy aún"
fi

# PASO 2: ESPERAR INICIALIZACIÓN COMPLETA
echo ""
echo "⏰ PASO 2: ESPERANDO INICIALIZACIÓN COMPLETA"
echo "==========================================="

log_info "Dando tiempo adicional para inicialización completa (60 segundos)..."
for i in {1..12}; do
    echo "   Esperando... $((i*5)) segundos"
    sleep 5
done

# PASO 3: VERIFICACIÓN DETALLADA DE ENDPOINTS
echo ""
echo "🧪 PASO 3: VERIFICACIÓN DETALLADA DE ENDPOINTS"
echo "=============================================="

# Función para verificar endpoint con más detalles
check_endpoint_detailed() {
    local name=$1
    local url=$2
    
    echo ""
    echo "🔍 Verificando $name:"
    echo "   URL: $url"
    
    # Usar curl con más opciones de debug
    response=$(curl -s -w "HTTP_CODE:%{http_code}\nTIME:%{time_total}\n" "$url" 2>&1)
    
    # Extraer información
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    time_total=$(echo "$response" | grep "TIME:" | cut -d: -f2)
    response_body=$(echo "$response" | grep -v "HTTP_CODE:" | grep -v "TIME:")
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ Status: $http_code (Tiempo: ${time_total}s)"
        echo "   📄 Response: ${response_body:0:100}..."
        return 0
    else
        echo "   ❌ Status: $http_code"
        echo "   📄 Error: $response_body"
        return 1
    fi
}

# Verificar cada endpoint
services_ok=0

if check_endpoint_detailed "Gateway Health" "http://localhost:8000/health"; then
    ((services_ok++))
fi

if check_endpoint_detailed "Auth Service Health" "http://localhost:8001/health"; then
    ((services_ok++))
fi

if check_endpoint_detailed "Product Service Health" "http://localhost:8002/health"; then
    ((services_ok++))
fi

if check_endpoint_detailed "Business Rules Health" "http://localhost:8003/health"; then
    ((services_ok++))
fi

echo ""
echo "📊 RESULTADO: $services_ok/4 servicios respondiendo"

# PASO 4: VERIFICAR ENDPOINTS ESPECÍFICOS
if [ $services_ok -ge 3 ]; then
    echo ""
    echo "🚀 PASO 4: VERIFICANDO ENDPOINTS ESPECÍFICOS"
    echo "==========================================="
    
    # Verificar endpoints del gateway
    echo ""
    echo "🌐 Verificando endpoints a través del gateway:"
    
    endpoints=(
        "Root:/"
        "Docs:/docs"
        "Configurations:/configurations"
        "Calculation Params:/calculations/params"
        "Insumos:/insumos"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        endpoint_name="${endpoint_info%%:*}"
        endpoint_path="${endpoint_info##*:}"
        
        echo ""
        echo "🔍 $endpoint_name ($endpoint_path):"
        
        response=$(curl -s -w "HTTP_CODE:%{http_code}\n" "http://localhost:8000$endpoint_path" 2>&1)
        http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
        response_body=$(echo "$response" | grep -v "HTTP_CODE:")
        
        if [ "$http_code" = "200" ]; then
            echo "   ✅ OK"
        elif [ "$http_code" = "404" ]; then
            echo "   ⚠️  Not Found (puede ser normal para algunos endpoints)"
        else
            echo "   ❌ Status: $http_code"
        fi
    done
fi

# PASO 5: RESUMEN Y SIGUIENTES PASOS
echo ""
echo "🎉 PASO 5: RESUMEN Y SIGUIENTES PASOS"
echo "===================================="

if [ $services_ok -eq 4 ]; then
    log_success "🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!"
    echo ""
    echo "✅ TODOS LOS SERVICIOS ESTÁN FUNCIONANDO:"
    echo "  • Gateway: http://localhost:8000"
    echo "  • Auth Service: http://localhost:8001"  
    echo "  • Product Service: http://localhost:8002"
    echo "  • Business Rules: http://localhost:8003"
    echo "  • MongoDB: localhost:27018"
    echo ""
    echo "🌐 ENDPOINTS PRINCIPALES:"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • Frontend: http://localhost:3000"
    echo ""
    echo "🚀 SIGUIENTE PASO:"
    echo "  ./initialize_business_data_fixed.sh"
    
elif [ $services_ok -ge 2 ]; then
    log_warning "⚠️ Sistema parcialmente funcional ($services_ok/4 servicios)"
    echo ""
    echo "💡 RECOMENDACIONES:"
    echo "  • Los servicios están healthy en Docker"
    echo "  • Puede necesitar más tiempo de inicialización"
    echo "  • Intentar acceder manualmente a las URLs"
    echo "  • Verificar logs si persisten problemas"
    
else
    log_error "❌ Sistema con problemas significativos"
    echo ""
    echo "🔍 DIAGNÓSTICO RECOMENDADO:"
    echo "  docker-compose logs api-gateway"
    echo "  docker-compose logs business-rules-service"
    echo "  docker-compose restart"
fi

echo ""
echo "🌐 URLs PARA VERIFICACIÓN MANUAL:"
echo "================================"
echo "• Gateway Root: http://localhost:8000"
echo "• Gateway Health: http://localhost:8000/health" 
echo "• Gateway Docs: http://localhost:8000/docs"
echo "• Business Rules: http://localhost:8003"
echo "• Business Rules Health: http://localhost:8003/health"
echo "• Auth Service: http://localhost:8001/health"
echo "• Product Service: http://localhost:8002/health"

echo ""
echo "📋 COMANDOS ÚTILES:"
echo "=================="
echo "• Ver logs: docker-compose logs [servicio]"
echo "• Reiniciar: docker-compose restart"
echo "• Estado: docker-compose ps"
echo "• Parar todo: docker-compose down"
echo "• Rebuildar: docker-compose build --no-cache"

echo ""
log_info "Verificación completada a las $(date)"