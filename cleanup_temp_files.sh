#!/bin/bash
echo "🧹 LIMPIANDO ARCHIVOS TEMPORALES Y ORGANIZANDO PROYECTO"
echo "====================================================="

# 1. Eliminar archivos temporales de fix
rm -f auth-service/Dockerfile.temp
rm -f auth-service/Dockerfile.fixed
rm -f auth-service/Dockerfile.bak
rm -f auth-service/.env.clean
rm -f auth-service/src/core/config_fixed.py

# 2. Eliminar scripts de diagnóstico temporales
rm -f diagnose_auth_error.sh
rm -f manual_diagnostic.sh
rm -f audit_step1.sh
rm -f security_audit_step2.sh
rm -f functionality_audit_step3.sh
rm -f testing_doc_audit_step4.sh
rm -f final_audit_summary.sh
rm -f start_security_fixes.sh
rm -f fix_auth_config.sh

# 3. Crear directorio de scripts útiles
mkdir -p scripts/diagnostics
mkdir -p scripts/deployment
mkdir -p scripts/development
mkdir -p scripts/testing

# 4. Mover scripts útiles a su lugar
mv initialize_business_data_fixed.sh scripts/development/ 2>/dev/null || true
mv test_complete_system.sh scripts/testing/ 2>/dev/null || true
mv generate_secrets.py scripts/deployment/ 2>/dev/null || true

echo "✅ Archivos temporales eliminados"
echo "✅ Scripts organizados en carpetas"
