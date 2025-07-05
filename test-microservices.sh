#!/bin/bash

echo "🧪 Testing Vel Arte Microservices..."

# Configuración
GATEWAY_URL="http://localhost:8000"
AUTH_URL="http://localhost:8001"

# Función para hacer peticiones
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_code=$4
    local description=$5
    
    echo -n "🔍 $description: "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X $method "$url")
    else
        response=$(curl -s -w "%{http_code}" -H "Content-Type: application/json" -X $method -d "$data" "$url")
    fi
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" -eq "$expected_code" ]; then
        echo "✅ OK ($http_code)"
    else
        echo "❌ FAIL ($http_code expected $expected_code)"
        echo "   Response: $body"
    fi
}

# Tests de salud
echo ""
echo "🏥 Health Checks:"
test_endpoint "GET" "$GATEWAY_URL/health" "" 200 "API Gateway Health"
test_endpoint "GET" "$AUTH_URL/health" "" 200 "Auth Service Health"

# Test de autenticación
echo ""
echo "🔐 Autenticación:"

# Login
login_data='{"username":"admin","password":"admin123"}'
login_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" "$GATEWAY_URL/auth/login")

if echo "$login_response" | grep -q "access_token"; then
    echo "✅ Login: OK"
    token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   Token obtenido: ${token:0:20}..."
else
    echo "❌ Login: FAIL"
    echo "   Response: $login_response"
    exit 1
fi

# Test de endpoints protegidos
echo ""
echo "🔒 Endpoints Protegidos:"

# Crear molde
molde_data='{"nombre":"Molde Test","material":"Silicona","peso":100,"precio_base":25000,"categoria":"Test"}'
create_molde_response=$(curl -s -H "Authorization: Bearer $token" -H "Content-Type: application/json" -X POST -d "$molde_data" "$GATEWAY_URL/moldes")

if echo "$create_molde_response" | grep -q "Molde Test"; then
    echo "✅ Crear molde: OK"
else
    echo "❌ Crear molde: FAIL"
    echo "   Response: $create_molde_response"
fi

# Listar moldes
list_moldes_response=$(curl -s -H "Authorization: Bearer $token" "$GATEWAY_URL/moldes")

if echo "$list_moldes_response" | grep -q "\["; then
    echo "✅ Listar moldes: OK"
    molde_count=$(echo "$list_moldes_response" | grep -o "\"id\":" | wc -l)
    echo "   Moldes encontrados: $molde_count"
else
    echo "❌ Listar moldes: FAIL"
    echo "   Response: $list_moldes_response"
fi

echo ""
echo "🎉 Testing completado!"
