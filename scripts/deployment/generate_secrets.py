#!/usr/bin/env python3
"""Generate secure secrets for .env files"""
import secrets
import string
import os

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file(service_name, env_example_path, env_path):
    """Create .env file from .env.example with real secrets"""
    if not os.path.exists(env_example_path):
        print(f"⚠️  {env_example_path} not found")
        return
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Replace secret placeholders
    content = content.replace('your-secret-key-here-change-in-production', generate_secret_key())
    content = content.replace('root:example', f'root:{generate_secret_key(32)}')
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created {env_path} with secure secrets")

# Generate .env files for all services
services = ['auth-service', 'product-service', 'business-rules-service', 'api-gateway']
for service in services:
    create_env_file(
        service,
        f'./{service}/.env.example',
        f'./{service}/.env'
    )

# Create root .env for docker-compose
with open('.env', 'w') as f:
    f.write(f"""# MongoDB Root Credentials
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD={generate_secret_key(32)}
MONGO_INITDB_DATABASE=vel_arte

# JWT Secret (shared across services)
JWT_SECRET={generate_secret_key()}

# Environment
ENVIRONMENT=development
""")

print("✅ Root .env created")
print("\n🔒 IMPORTANT: Never commit .env files to git!")
