# backend/services/cache_service.py
import json
from backend.database.connection import get_redis_connection

def get_from_cache(key):
    """Obtiene datos del cache de Redis"""
    redis_client = get_redis_connection()
    cached_data = redis_client.get(key)
    return json.loads(cached_data) if cached_data else None

def set_to_cache(key, data, expiration=3600):
    """Guarda datos en el cache de Redis"""
    redis_client = get_redis_connection()
    redis_client.setex(key, expiration, json.dumps(data))
    return True