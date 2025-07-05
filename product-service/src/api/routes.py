from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.models.product import MoldeCreate, MoldeResponse, ProductoCreate, ProductoResponse
from src.services.product_service import ProductService
from src.services.auth_client import verify_token  # ← LÍNEA CAMBIADA

router = APIRouter()

@router.post("/moldes", response_model=MoldeResponse)
async def create_molde(molde: MoldeCreate, user=Depends(verify_token)):
    return await ProductService.create_molde(molde)

@router.get("/moldes", response_model=List[MoldeResponse])
async def get_moldes():
    return await ProductService.get_moldes()

@router.get("/moldes/{molde_id}", response_model=MoldeResponse)
async def get_molde(molde_id: str):
    molde = await ProductService.get_molde_by_id(molde_id)
    if not molde:
        raise HTTPException(status_code=404, detail="Molde no encontrado")
    return molde

@router.post("/productos", response_model=ProductoResponse)
async def create_producto(producto: ProductoCreate, user=Depends(verify_token)):
    return await ProductService.create_producto(producto)
