from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vel Arte - pricing-service",
    description="Servicio de pricing-service",
    version="1.0.0"
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
    return {"status": "healthy", "service": "pricing-service"}

@app.get("/")
async def root():
    return {"message": "pricing-service funcionando", "version": "1.0.0"}
