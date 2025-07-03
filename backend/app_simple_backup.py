from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Sistema de Gestión de Velas Vel Arte",
    version="1.0.0",
    description="🕯️ Sistema web para gestión de velas artesanales"
)

@app.get("/")
def home():
    return {
        "message": "🎉 ¡Bienvenido al Sistema de Velas Vel Arte!",
        "empresa": "Vel Arte",
        "desarrollador": "Carlos T",
        "status": "✅ FastAPI funcionando correctamente",
        "version": "1.0.0"
    }

@app.get("/velas")
def productos_velas():
    return {
        "productos_disponibles": [
            {"codigo": "VA001", "nombre": "Vela Aromática Lavanda", "precio": 15000},
            {"codigo": "VA002", "nombre": "Vela Decorativa Rosa", "precio": 18000},
            {"codigo": "VA003", "nombre": "Vela Personalizada", "precio": 25000}
        ],
        "materiales": ["Cera de soja", "Fragancia natural", "Pabilo de algodón"],
        "estado": "En desarrollo"
    }

@app.get("/insumos")
def lista_insumos():
    return {
        "insumos_principales": [
            {"codigo": "CV001", "descripcion": "Cera de Vaso", "costo_kg": 28000},
            {"codigo": "FR001", "descripcion": "Fragancia", "costo_ml": 300},
            {"codigo": "CL001", "descripcion": "Colorante", "costo_gota": 50},
            {"codigo": "PB001", "descripcion": "Pabilo", "costo_unidad": 10}
        ],
        "total_insumos": 4,
        "estado": "Simulado (sin base de datos)"
    }

@app.get("/health")
def check_health():
    return {
        "status": "healthy",
        "fastapi": "✅ Funcionando",
        "mongodb": "🔄 En configuración",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("🚀 Iniciando Sistema de Velas en http://localhost:8000")
    print("📚 Documentación en http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
