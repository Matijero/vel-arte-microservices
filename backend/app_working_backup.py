from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

# Modelos
class Insumo(BaseModel):
    codigo: str
    descripcion: str
    costo: float
    cantidad: int = 1
    activo: bool = True

class InsumoCreate(BaseModel):
    codigo: str
    descripcion: str
    costo: float
    cantidad: int = 1

# Base de datos simulada
insumos_db: Dict[str, Insumo] = {
    "CV001": Insumo(codigo="CV001", descripcion="CERA DE VASO", costo=28000, cantidad=50),
    "FR001": Insumo(codigo="FR001", descripcion="FRAGANCIA", costo=6000, cantidad=20),
    "CL001": Insumo(codigo="CL001", descripcion="COLORANTE", costo=5000, cantidad=30),
    "PB001": Insumo(codigo="PB001", descripcion="PABILO", costo=1700, cantidad=100),
}

# Aplicación FastAPI
app = FastAPI(
    title="Sistema CRUD Velas Vel Arte",
    version="2.0.0",
    description="Sistema completo con operaciones CRUD"
)

@app.get("/")
def home():
    return {
        "message": "Sistema CRUD Completo Funcionando",
        "version": "2.0.0", 
        "metodos_disponibles": ["GET", "POST", "PUT", "DELETE"],
        "total_insumos": len(insumos_db)
    }

@app.get("/insumos", response_model=List[Insumo])
def listar_insumos():
    """Obtener lista de todos los insumos"""
    return list(insumos_db.values())

@app.get("/insumos/{codigo}", response_model=Insumo)
def obtener_insumo(codigo: str):
    """Obtener un insumo específico por código"""
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    return insumos_db[codigo]

@app.post("/insumos", response_model=Insumo)
def crear_insumo(insumo: InsumoCreate):
    """Crear un nuevo insumo"""
    if insumo.codigo in insumos_db:
        raise HTTPException(status_code=400, detail=f"El insumo {insumo.codigo} ya existe")
    
    nuevo_insumo = Insumo(**insumo.dict())
    insumos_db[insumo.codigo] = nuevo_insumo
    return nuevo_insumo

@app.put("/insumos/{codigo}", response_model=Insumo)
def actualizar_insumo(codigo: str, insumo_data: dict):
    """Actualizar un insumo existente"""
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    
    insumo = insumos_db[codigo]
    for key, value in insumo_data.items():
        if hasattr(insumo, key):
            setattr(insumo, key, value)
    
    return insumo

@app.delete("/insumos/{codigo}")
def eliminar_insumo(codigo: str):
    """Eliminar un insumo"""
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail=f"Insumo {codigo} no encontrado")
    
    insumo_eliminado = insumos_db[codigo]
    del insumos_db[codigo]
    
    return {
        "message": f"Insumo {codigo} eliminado correctamente",
        "insumo_eliminado": insumo_eliminado,
        "total_restante": len(insumos_db)
    }

if __name__ == "__main__":
    print("Iniciando Sistema CRUD de Velas...")
    print("URL: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)