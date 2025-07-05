from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vel Arte Business Rules Service", 
    version="1.0.0",
    description="Microservicio para reglas de negocio y cálculos de costos"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "business-rules-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Vel Arte Business Rules Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/docs"
        ]
    }

# Endpoints básicos para testing
@app.get("/configurations")
async def get_configurations():
    return {
        "message": "Configurations endpoint - Basic implementation",
        "configurations": []
    }

@app.post("/configurations/initialize")
async def initialize_configurations():
    return {
        "message": "Configurations initialized (basic)",
        "count": 0
    }

@app.get("/calculations/params")
async def get_calculation_params():
    return {
        "message": "Calculation params endpoint - Basic implementation",
        "parametros": {
            "porcentajes": {
                "aditivo": 8.0,
                "fragancia": 6.0,
                "ganancia": 250.0,
                "detalle": 20.0,
                "admin": 10.0
            },
            "precios_insumos": {
                "cera_kg": 15000,
                "aditivo_kg": 8000,
                "fragancia_ml": 150,
                "colorante_gota": 50,
                "pabilo_metro": 200
            },
            "redondeo": {
                "multiplo": 500
            },
            "descuentos_cantidad": {}
        }
    }
