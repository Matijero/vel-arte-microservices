from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import uuid

# Modelo básico para empezar
class Insumo(BaseModel):
    id: str = None
    codigo: str
    descripcion: str
    costo: float
    cantidad: int = 1
    activo: bool = True

# Base de datos en memoria
insumos_db: Dict[str, Insumo] = {
    "CV001": Insumo(id="1", codigo="CV001", descripcion="CERA DE VASO", costo=28000, cantidad=50),
    "FR001": Insumo(id="2", codigo="FR001", descripcion="FRAGANCIA", costo=6000, cantidad=20),
}

app = FastAPI(title="🕯️ Sistema CRUD Velas Vel Arte", version="2.0.0")

@app.get("/")
def home():
    return {
        "message": "🎉 Sistema CRUD Completo de Velas",
        "version": "2.0.0",
        "metodos": ["GET", "POST", "PUT", "DELETE"],
        "total_insumos": len(insumos_db)
    }

# CRUD Insumos
@app.get("/insumos", response_model=List[Insumo])
def listar_insumos():
    return list(insumos_db.values())

@app.get("/insumos/{codigo}")
def obtener_insumo(codigo: str):
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return insumos_db[codigo]

@app.post("/insumos")
def crear_insumo(insumo: Insumo):
    if insumo.codigo in insumos_db:
        raise HTTPException(status_code=400, detail="Insumo ya existe")
    
    insumo.id = str(uuid.uuid4())
    insumos_db[insumo.codigo] = insumo
    return {"message": f"Insumo {insumo.codigo} creado", "insumo": insumo}

@app.put("/insumos/{codigo}")
def actualizar_insumo(codigo: str, insumo_update: dict):
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    insumo = insumos_db[codigo]
    for key, value in insumo_update.items():
        if hasattr(insumo, key):
            setattr(insumo, key, value)
    
    return {"message": f"Insumo {codigo} actualizado", "insumo": insumo}

@app.delete("/insumos/{codigo}")
def eliminar_insumo(codigo: str):
    if codigo not in insumos_db:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    
    del insumos_db[codigo]
    return {"message": f"Insumo {codigo} eliminado"}

if __name__ == "__main__":
    print("🚀 Sistema CRUD Completo iniciando en http://localhost:8000")
    print("📚 Documentación en http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
