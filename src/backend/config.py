# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración Redis
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'password': os.getenv('REDIS_PASSWORD'),
    'decode_responses': True
}

# Configuración PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'database': os.getenv('POSTGRES_DB', 'pokedex_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
    'port': os.getenv('POSTGRES_PORT', 5432)
}

# Configuración FastAPI
FASTAPI_CONFIG = {
    'title': 'Pokédex API',
    'version': '1.0.0',
    'host': os.getenv('HOST', '0.0.0.0'),
    'port': int(os.getenv('PORT', 8000)),
    'reload': os.getenv('RELOAD', 'false').lower() == 'true'  # Default to false
}

# CORS
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', "http://localhost:5500,http://localhost:3000").split(",")