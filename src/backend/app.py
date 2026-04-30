# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import FASTAPI_CONFIG, ALLOWED_ORIGINS
from backend.routes import pokemon_routes, health_routes

# Crear aplicación
app = FastAPI(
    title=FASTAPI_CONFIG['title'],
    version=FASTAPI_CONFIG['version']
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Incluir routers
app.include_router(pokemon_routes.router)
app.include_router(health_routes.router)

# Endpoint raíz
@app.get("/")
async def read_root():
    return {
        "message": "Pokédex API is running!",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "pokemon": "/api/pokemon/{name}",
            "docs": "/docs"
        }
    }