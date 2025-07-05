#!/bin/bash
# 📄 SCRIPT 2: verify_system.sh
# Verifica que todos los servicios estén funcionando correctamente

echo "✅ VERIFICACIÓN COMPLETA DEL SISTEMA"
echo "==================================="
echo "⏰ $(date)"
echo ""

# Función para verificar endpoint
check_endpoint() {
    local name=$1
    local url=$2
    
    echo -n "🔍 $name: "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

# Función para mostrar respuesta de endpoint
show_endpoint_response() {
    local name=$1
    local url=$2
    
    echo ""
    echo "📊 $name:"
    local response=$(curl -s "$url" 2>/dev/null)
    if [ -n "$response" ]; then
        echo "$response"
    else
        echo "No disponible"
    fi
    echo ""
}

echo "🌐 VERIFICANDO CONECTIVIDAD BÁSICA"
echo "=================================="

# Verificar cada servicio
working=0

if check_endpoint "Gateway (8000)" "http://localhost:8000/health"; then
    ((working++))
fi

if check_endpoint "Auth Service (8001)" "http://localhost:8001/health"; then
    ((working++))
fi

if check_endpoint "Product Service (8002)" "http://localhost:8002/health"; then
    ((working++))
fi

if check_endpoint "Business Rules (8003)" "http://localhost:8003/health"; then
    ((working++))
fi

echo ""
echo "📊 RESULTADO: $working/4 servicios funcionando"

if [ $working -eq 4 ]; then
    echo "🎉 ¡TODOS LOS SERVICIOS ESTÁN FUNCIONANDO!"
    
    echo ""
    echo "🧪 VERIFICANDO ENDPOINTS ESPECÍFICOS"
    echo "===================================="
    
    # Verificar endpoints específicos
    check_endpoint "Configurations" "http://localhost:8000/configurations"
    check_endpoint "Calculation Params" "http://localhost:8000/calculations/params" 
    check_endpoint "Insumos" "http://localhost:8000/insumos"
    check_endpoint "Auth Login" "http://localhost:8000/auth/register"
    
    # Mostrar respuestas detalladas
    show_endpoint_response "Gateway Health" "http://localhost:8000/health"
    show_endpoint_response "Business Rules Health" "http://localhost:8003/health"
    
    echo "🌐 ENDPOINTS DISPONIBLES:"
    echo "  • API Gateway: http://localhost:8000"
    echo "  • Documentación: http://localhost:8000/docs"
    echo "  • Auth Service: http://localhost:8001"
    echo "  • Product Service: http://localhost:8002" 
    echo "  • Business Rules: http://localhost:8003"
    echo "  • Frontend: http://localhost:3000"
    
    echo ""
    echo "✅ SISTEMA LISTO - SIGUIENTE PASO:"
    echo "  ./initialize_business_data_fixed.sh"
    
elif [ $working -gt 0 ]; then
    echo "⚠️  ALGUNOS SERVICIOS FUNCIONANDO"
    echo ""
    echo "🔍 VERIFICANDO LOGS:"
    echo "docker-compose logs business-rules-service"
    echo "docker-compose logs api-gateway"
    
    echo ""
    echo "💡 POSIBLES SOLUCIONES:"
    echo "   - Esperar 1-2 minutos más"
    echo "   - Ejecutar: docker-compose restart"
    echo "   - Ver logs específicos del servicio que falla"
    
else
    echo "❌ NINGÚN SERVICIO FUNCIONANDO"
    echo ""
    echo "🔍 DIAGNÓSTICO:"
    echo "   - docker-compose ps"
    echo "   - docker-compose logs"
    echo ""
    echo "🔄 SOLUCIÓN:"
    echo "   docker-compose down && docker-compose up -d"
fi

echo ""
echo "🐳 ESTADO ACTUAL DE CONTENEDORES:"
docker-compose ps

echo ""
echo "📋 COMANDOS ÚTILES:"
echo "  • Ver logs: docker-compose logs [servicio]"
echo "  • Reiniciar: docker-compose restart [servicio]"  
echo "  • Rebuild: docker-compose build --no-cache [servicio]"
echo "  • Estado: docker-compose ps"