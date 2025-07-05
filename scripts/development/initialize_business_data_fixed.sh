#!/bin/bash
# 📄 SCRIPT 3: initialize_business_data_fixed.sh
# Inicializa las configuraciones de negocio en el sistema

echo "🔧 INICIALIZANDO DATOS DE NEGOCIO"
echo "================================="
echo "⏰ $(date)"
echo ""

API_BASE="http://localhost:8000"

# Función para hacer request y mostrar resultado
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo "📝 $description"
    echo "   URL: $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\nHTTP_STATUS:%{http_code}")
    else
        response=$(curl -s -X "$method" "$url" \
            -w "\nHTTP_STATUS:%{http_code}")
    fi
    
    # Extraer status code
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    response_body=$(echo "$response" | grep -v "HTTP_STATUS:")
    
    if [ "$http_status" = "200" ] || [ "$http_status" = "201" ]; then
        echo "   ✅ Status: $http_status"
        echo "   📄 Response: $response_body"
    else
        echo "   ❌ Status: $http_status"
        echo "   📄 Error: $response_body"
    fi
    echo ""
}

echo "🌐 PASO 1: VERIFICANDO CONECTIVIDAD"
echo "==================================="

# Verificar que el sistema esté funcionando
echo "🔍 Verificando gateway..."
if curl -s -f "$API_BASE/health" > /dev/null 2>&1; then
    echo "✅ Gateway responde"
else
    echo "❌ Gateway no responde"
    echo "💡 Ejecuta primero: ./fix_build_errors.sh"
    exit 1
fi

echo "🔍 Verificando business rules service..."
if curl -s -f "http://localhost:8003/health" > /dev/null 2>&1; then
    echo "✅ Business rules service responde"
else
    echo "❌ Business rules service no responde"
    echo "💡 Verifica: docker-compose logs business-rules-service"
    exit 1
fi

echo ""
echo "🔧 PASO 2: INICIALIZANDO CONFIGURACIONES"
echo "========================================"

make_request "POST" "$API_BASE/configurations/initialize" "" "Inicializando configuraciones por defecto"

echo ""
echo "🎁 PASO 3: AGREGANDO DESCUENTOS POR CANTIDAD"
echo "============================================"

# Descuento 5% para 10+ unidades
descuento_10='{
    "key": "descuento_10",
    "name": "Descuento 10+ unidades",
    "description": "5% de descuento para 10 o más unidades",
    "value": "5.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
}'

make_request "POST" "$API_BASE/configurations" "$descuento_10" "Creando descuento 10+ unidades (5%)"

# Descuento 10% para 20+ unidades
descuento_20='{
    "key": "descuento_20",
    "name": "Descuento 20+ unidades", 
    "description": "10% de descuento para 20 o más unidades",
    "value": "10.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
}'

make_request "POST" "$API_BASE/configurations" "$descuento_20" "Creando descuento 20+ unidades (10%)"

# Descuento 15% para 50+ unidades
descuento_50='{
    "key": "descuento_50",
    "name": "Descuento 50+ unidades",
    "description": "15% de descuento para 50 o más unidades", 
    "value": "15.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
}'

make_request "POST" "$API_BASE/configurations" "$descuento_50" "Creando descuento 50+ unidades (15%)"

echo ""
echo "📊 PASO 4: VERIFICANDO CONFIGURACIONES CARGADAS"
echo "==============================================="

echo "📝 Obteniendo todas las configuraciones..."
response=$(curl -s "$API_BASE/configurations" -w "\nHTTP_STATUS:%{http_code}")
http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
response_body=$(echo "$response" | grep -v "HTTP_STATUS:")

if [ "$http_status" = "200" ]; then
    echo "✅ Status: $http_status"
    echo "📄 Configuraciones encontradas:"
    echo "$response_body"
else
    echo "❌ Status: $http_status"
    echo "📄 Error: $response_body"
fi
echo ""

echo ""
echo "🧮 PASO 5: VERIFICANDO PARÁMETROS DE CÁLCULO"
echo "============================================"

make_request "GET" "$API_BASE/calculations/params" "" "Obteniendo parámetros de cálculo actuales"

echo ""
echo "🧪 PASO 6: PROBANDO ACTUALIZACIÓN DE CONFIGURACIÓN"
echo "=================================================="

# Probar actualización de una configuración
echo "📝 Actualizando porcentaje de ganancia a 280%..."

# Nota: La API puede requerir parámetros de query en lugar de JSON body
update_response=$(curl -s -X PUT "$API_BASE/configurations/porc_ganancia?new_value=280&user_id=admin&reason=Test%20de%20inicializacion" \
    -H "Content-Type: application/json" \
    -w "\nHTTP_STATUS:%{http_code}")

http_status=$(echo "$update_response" | grep "HTTP_STATUS:" | cut -d: -f2)
response_body=$(echo "$update_response" | grep -v "HTTP_STATUS:")

if [ "$http_status" = "200" ]; then
    echo "✅ Configuración actualizada exitosamente"
    echo "📄 Response: $response_body"
else
    echo "❌ Error actualizando configuración (Status: $http_status)"
    echo "📄 Error: $response_body"
fi

echo ""
echo "📈 PASO 7: VERIFICANDO HISTÓRICO DE CAMBIOS"
echo "==========================================="

make_request "GET" "$API_BASE/configurations/porc_ganancia/history" "" "Obteniendo histórico de cambios"

echo ""
echo "🎉 INICIALIZACIÓN COMPLETADA"
echo "============================"

echo "✅ Pasos ejecutados:"
echo "  • Configuraciones por defecto cargadas"
echo "  • Descuentos por cantidad configurados"
echo "  • Parámetros de cálculo verificados"
echo "  • Test de actualización realizado"
echo "  • Histórico de cambios verificado"

echo ""
echo "🌐 URLs de verificación manual:"
echo "  • Gateway: http://localhost:8000"
echo "  • Configuraciones: http://localhost:8000/configurations"
echo "  • Parámetros: http://localhost:8000/calculations/params"
echo "  • Documentación: http://localhost:8000/docs"
echo "  • Frontend: http://localhost:3000"

echo ""
echo "🚀 SIGUIENTE PASO:"
echo "  ./test_complete_system.sh  # Para testing completo"
echo "  O continuar con frontend y preparar para GitHub"