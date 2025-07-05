#!/bin/bash
echo "🔧 INICIALIZANDO DATOS DE NEGOCIO"
echo "================================="

API_BASE="http://localhost:8000"

echo "1. Inicializando configuraciones por defecto..."
curl -X POST "$API_BASE/configurations/initialize" \
  -H "Content-Type: application/json" \
  -s | jq '.'

echo -e "\n2. Agregando descuentos por cantidad..."

# Descuento 5% para 10+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_10",
    "name": "Descuento 10+ unidades",
    "description": "5% de descuento para 10 o más unidades",
    "value": "5.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

# Descuento 10% para 20+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_20",
    "name": "Descuento 20+ unidades",
    "description": "10% de descuento para 20 o más unidades",
    "value": "10.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

# Descuento 15% para 50+ unidades
curl -X POST "$API_BASE/configurations" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "descuento_50",
    "name": "Descuento 50+ unidades",
    "description": "15% de descuento para 50 o más unidades",
    "value": "15.0",
    "type": "percentage",
    "category": "descuentos_cantidad"
  }' -s | jq '.'

echo -e "\n3. Creando moldes de ejemplo..."

# TODO: Implementar creación de moldes via API

echo -e "\n4. Creando productos de ejemplo..."

# TODO: Implementar creación de productos via API

echo -e "\n5. Probando cálculo de ejemplo..."
# curl -X POST "$API_BASE/calculations/product/PRODUCTO_ID?cantidad_gotas=3" -s | jq '.'

echo -e "\n✅ Inicialización completada!"
echo "📊 Ver configuraciones: curl $API_BASE/configurations | jq '.'"
echo "🧮 Ver parámetros: curl $API_BASE/calculations/params | jq '.'"
