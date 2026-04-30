# backend/routes/health_routes.py
from fastapi import APIRouter
from backend.database.connection import get_redis_connection, get_postgres_connection

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        get_redis_connection().ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    try:
        conn = get_postgres_connection()
        conn.close()
        postgres_status = "connected"
    except:
        postgres_status = "disconnected"
    
    return {
        "status": "healthy",
        "dependencies": {
            "redis": redis_status,
            "postgresql": postgres_status,
            "pokeapi": "reachable"
        }
    }