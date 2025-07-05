#!/usr/bin/env python3
"""
Script para migrar datos del sistema monolítico a microservicios
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from datetime import datetime

# Configuración
MONGO_URL = "mongodb://admin:password123@localhost:27017"
EXCEL_FILE = "../backend/costos velas.xlsx"

async def migrate_moldes():
    """Migrar moldes desde Excel a product-service"""
    client = AsyncIOMotorClient(f"{MONGO_URL}/vel_arte_products?authSource=admin")
    db = client.get_default_database()
    
    try:
        # Leer Excel
        df = pd.read_excel(EXCEL_FILE, sheet_name="Moldes")
        
        moldes_data = []
        for _, row in df.iterrows():
            molde = {
                "nombre": row.get("Nombre", ""),
                "material": row.get("Material", "Silicona"),
                "peso": float(row.get("Peso", 0)),
                "precio_base": float(row.get("Precio", 0)),
                "categoria": row.get("Categoria", "General"),
                "disponible": True,
                "created_at": datetime.utcnow()
            }
            moldes_data.append(molde)
        
        # Insertar en MongoDB
        if moldes_data:
            result = await db.moldes.insert_many(moldes_data)
            print(f"✅ Migrados {len(result.inserted_ids)} moldes")
        
    except Exception as e:
        print(f"❌ Error migrando moldes: {e}")
    finally:
        client.close()

async def migrate_users():
    """Crear usuarios iniciales en auth-service"""
    client = AsyncIOMotorClient(f"{MONGO_URL}/vel_arte_auth?authSource=admin")
    db = client.get_default_database()
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    users = [
        {
            "username": "admin",
            "email": "admin@velarte.com",
            "full_name": "Administrador",
            "role": "admin",
            "password": pwd_context.hash("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "username": "operador",
            "email": "operador@velarte.com", 
            "full_name": "Operador",
            "role": "operator",
            "password": pwd_context.hash("op123"),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    try:
        for user in users:
            existing = await db.users.find_one({"username": user["username"]})
            if not existing:
                await db.users.insert_one(user)
                print(f"✅ Usuario creado: {user['username']}")
            else:
                print(f"ℹ️  Usuario ya existe: {user['username']}")
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
    finally:
        client.close()

async def main():
    print("🔄 Iniciando migración a microservicios...")
    
    await migrate_users()
    await migrate_moldes()
    
    print("✅ Migración completada!")

if __name__ == "__main__":
    asyncio.run(main())
