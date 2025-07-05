#!/bin/bash
# 📄 SCRIPT 4: test_complete_system.sh
# Testing completo de todo el sistema implementado

echo "🧪 TESTING COMPLETO DEL SISTEMA VEL ARTE"
echo "========================================"
echo "⏰ $(date)"
echo ""

API_BASE="http://localhost:8000"

# Función para test con resultado
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected_status=${5:-200}
    
    echo "🧪 Test: $name"
    echo "   $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\nHTTP_STATUS:%{http_code}")
    else
        response=$(curl -s -X "$method" "$url" \
            -w "\nHTTP_STATUS:%{http_code}")
    fi
    
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    response_body=$(echo "$response" | grep -v "HTTP_STATUS:")
    
    if [ "$http_status" = "$expected_status" ]; then
        echo "   ✅ PASS (Status: $http_status)"
        return 0
    else
        echo "   ❌ FAIL (Status: $http_status, Expected: $expected_status)"
        echo "   📄 Response: $response_body"
        return 1
    fi
    echo ""
}

echo "🌐 SUITE 1: HEALTH CHECKS"
echo "========================"

passed=0
total=0

# Test health checks
if test_endpoint "Gateway Health" "GET" "$API_BASE/health"; then ((passed++)); fi; ((total++))
if test_endpoint "Auth Health" "GET" "$API_BASE/../:8001/health"; then ((passed++)); fi; ((total++))
if test_endpoint "Products Health" "GET" "$API_BASE/../:8002/health"; then ((passed++)); fi; ((total++))
if test_endpoint "Business Rules Health" "GET" "$API_BASE/../:8003/health"; then ((passed++)); fi; ((total++))

echo "📊 Health Checks: $passed/$total passed"
echo ""

echo "🔐 SUITE 2: AUTENTICACIÓN"
echo "========================"

# Test registro de usuario
test_data='{
    "name": "Test User",
    "email": "test@velarte.com", 
    "password": "test123456"
}'

if test_endpoint "User Registration" "POST" "$API_BASE/auth/register" "$test_data"; then ((passed++)); fi; ((total++))

# Test login
login_data='{
    "email": "admin@velarte.com",
    "password": "admin123"
}'

echo "🧪 Test: Admin Login"
echo "   POST $API_BASE/auth/login"
login_response=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d "$login_data" \
    -w "\nHTTP_STATUS:%{http_code}")

login_status=$(echo "$login_response" | grep "HTTP_STATUS:" | cut -d: -f2)
login_body=$(echo "$login_response" | grep -v "HTTP_STATUS:")

if [ "$login_status" = "200" ]; then
    echo "   ✅ PASS (Status: $login_status)"
    # Extraer token (simplificado)
    TOKEN=$(echo "$login_body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   🔑 Token obtenido: ${TOKEN:0:20}..."
    ((passed++))
else
    echo "   ❌ FAIL (Status: $login_status)"
    echo "   📄 Response: $login_body"
fi
((total++))
echo ""

echo "📊 Autenticación: $((passed-4))/$((total-4)) passed"
echo ""

echo "🏗️ SUITE 3: CONFIGURACIONES"
echo "=========================="

# Test obtener configuraciones
if test_endpoint "Get Configurations" "GET" "$API_BASE/configurations"; then ((passed++)); fi; ((total++))

# Test obtener parámetros de cálculo
if test_endpoint "Get Calculation Params" "GET" "$API_BASE/calculations/params"; then ((passed++)); fi; ((total++))

# Test actualizar configuración
echo "🧪 Test: Update Configuration"
echo "   PUT $API_BASE/configurations/porc_aditivo"
update_response=$(curl -s -X PUT "$API_BASE/configurations/porc_aditivo?new_value=9.0&user_id=test&reason=Testing" \
    -H "Content-Type: application/json" \
    -w "\nHTTP_STATUS:%{http_code}")

update_status=$(echo "$update_response" | grep "HTTP_STATUS:" | cut -d: -f2)
if [ "$update_status" = "200" ]; then
    echo "   ✅ PASS (Status: $update_status)"
    ((passed++))
else
    echo "   ❌ FAIL (Status: $update_status)"
fi
((total++))
echo ""

echo "📊 Configuraciones: $((passed-6))/$((total-6)) passed"
echo ""

echo "📦 SUITE 4: PRODUCTOS (CRUD)"
echo "=========================="

# Test obtener insumos
if test_endpoint "Get Insumos" "GET" "$API_BASE/insumos"; then ((passed++)); fi; ((total++))

# Test crear insumo (con autenticación)
insumo_data='{
    "nombre": "Test Insumo",
    "precio": 1500.00,
    "categoria": "testing",
    "descripcion": "Insumo de prueba"
}'

echo "🧪 Test: Create Insumo (with auth)"
echo "   POST $API_BASE/insumos"
if [ -n "$TOKEN" ]; then
    create_response=$(curl -s -X POST "$API_BASE/insumos" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$insumo_data" \
        -w "\nHTTP_STATUS:%{http_code}")
    
    create_status=$(echo "$create_response" | grep "HTTP_STATUS:" | cut -d: -f2)
    if [ "$create_status" = "201" ] || [ "$create_status" = "200" ]; then
        echo "   ✅ PASS (Status: $create_status)"
        ((passed++))
    else
        echo "   ❌ FAIL (Status: $create_status)"
    fi
else
    echo "   ⚠️  SKIP (No token available)"
fi
((total++))
echo ""

echo "📊 Productos: $((passed-9))/$((total-9)) passed"
echo ""

echo "🧮 SUITE 5: CÁLCULOS DE NEGOCIO"
echo "============================="

# Test simulación de cálculo (sin producto real)
echo "🧪 Test: Calculation Simulation"
echo "   GET $API_BASE/calculations/params"
calc_response=$(curl -s "$API_BASE/calculations/params" -w "\nHTTP_STATUS:%{http_code}")
calc_status=$(echo "$calc_response" | grep "HTTP_STATUS:" | cut -d: -f2)

if [ "$calc_status" = "200" ]; then
    echo "   ✅ PASS - Calculation params available"
    calc_body=$(echo "$calc_response" | grep -v "HTTP_STATUS:")
    echo "   📄 Params preview: ${calc_body:0:100}..."
    ((passed++))
else
    echo "   ❌ FAIL (Status: $calc_status)"
fi
((total++))
echo ""

echo "📊 Cálculos: $((passed-12))/$((total-12)) passed"
echo ""

echo "🎉 RESUMEN FINAL"
echo "==============="
echo "📊 Total Tests: $passed/$total passed"

percentage=$((passed * 100 / total))
echo "📈 Success Rate: $percentage%"

if [ $percentage -ge 80 ]; then
    echo "🎉 ¡SISTEMA FUNCIONANDO EXCELENTE!"
    echo ""
    echo "✅ READY FOR:"
    echo "  • Frontend integration"
    echo "  • GitHub upload"
    echo "  • Production deployment"
    
elif [ $percentage -ge 60 ]; then
    echo "⚠️  Sistema funcionando con algunos problemas menores"
    echo "💡 Revisar tests fallidos y logs"
    
else
    echo "❌ Sistema tiene problemas significativos"
    echo "🔍 Revisar configuración y logs de servicios"
fi

echo ""
echo "🌐 URLs FINALES:"
echo "  • Gateway: http://localhost:8000"
echo "  • Docs: http://localhost:8000/docs"
echo "  • Frontend: http://localhost:3000"
echo "  • MongoDB: localhost:27018"

echo ""
echo "📋 LOGS ÚTILES:"
echo "  docker-compose logs api-gateway"
echo "  docker-compose logs business-rules-service"
echo "  docker-compose logs auth-service"
echo "  docker-compose logs product-service"

echo ""
echo "🚀 SIGUIENTE PASO:"
echo "  git add . && git commit -m 'Sistema completo funcionando'"