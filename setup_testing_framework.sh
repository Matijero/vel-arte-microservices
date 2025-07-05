#!/bin/bash
echo "🧪 CONFIGURANDO FRAMEWORK DE TESTING"

# 1. Actualizar requirements con herramientas de testing
cat >> requirements-dev.txt << 'REQUIREMENTS'
# Testing
pytest==8.4.1
pytest-asyncio==1.0.0
pytest-cov==5.0.0
pytest-mock==3.14.0
pytest-env==1.1.5
httpx==0.27.2

# Code Quality
black==24.10.0
flake8==7.1.1
pylint==3.3.2
mypy==1.13.0
isort==5.13.2
bandit==1.8.0

# Pre-commit
pre-commit==4.0.1
REQUIREMENTS

# 2. Crear pytest.ini
cat > pytest.ini << 'PYTEST'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
PYTEST

# 3. Crear test de ejemplo
mkdir -p auth-service/tests/unit/domain
cat > auth-service/tests/unit/domain/test_user_entity.py << 'TEST'
import pytest
from datetime import datetime
from src.domain.entities.user import User
from src.domain.value_objects import Email, UserId, HashedPassword

class TestUserEntity:
    def test_create_user(self):
        """Test crear usuario"""
        user = User(
            id=UserId("123"),
            email=Email("test@example.com"),
            username="testuser",
            hashed_password=HashedPassword("hashed123"),
            full_name="Test User"
        )
        
        assert user.id == "123"
        assert str(user.email) == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active == True
        assert user.is_superuser == False
    
    def test_deactivate_user(self):
        """Test desactivar usuario"""
        user = User(
            id=UserId("123"),
            email=Email("test@example.com"),
            username="testuser",
            hashed_password=HashedPassword("hashed123")
        )
        
        original_updated_at = user.updated_at
        user.deactivate()
        
        assert user.is_active == False
        assert user.updated_at > original_updated_at
    
    def test_invalid_email(self):
        """Test email inválido"""
        with pytest.raises(ValueError):
            Email("invalid-email")
TEST

echo "✅ Framework de testing configurado"
