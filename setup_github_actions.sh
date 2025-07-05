#!/bin/bash
echo "🚀 CONFIGURANDO GITHUB ACTIONS"

mkdir -p .github/workflows

# 1. CI Pipeline
cat > .github/workflows/ci.yml << 'CI'
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [auth-service, product-service, business-rules-service]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd ${{ matrix.service }}
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd ${{ matrix.service }}
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./${{ matrix.service }}/coverage.xml
        flags: ${{ matrix.service }}

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install linters
      run: |
        pip install black flake8 mypy
    
    - name: Run Black
      run: black --check .
    
    - name: Run Flake8
      run: flake8 .
    
    - name: Run MyPy
      run: mypy .

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker images
      run: |
        docker-compose build
    
    - name: Run integration tests
      run: |
        docker-compose up -d
        sleep 30
        ./scripts/testing/test_complete_system.sh
        docker-compose down
CI

# 2. CD Pipeline
cat > .github/workflows/cd.yml << 'CD'
name: CD Pipeline

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push images
      run: |
        docker-compose build
        docker-compose push
    
    - name: Deploy to production
      run: |
        echo "Deploy to production server"
        # Aquí agregar comandos de deployment
CD

echo "✅ GitHub Actions configurado"
