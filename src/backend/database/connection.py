# backend/database/connection.py
import redis
import psycopg2
from backend.config import REDIS_CONFIG, POSTGRES_CONFIG

def get_redis_connection():
    """Conexión a Redis"""
    return redis.Redis(**REDIS_CONFIG)

def get_postgres_connection():
    """Conexión a PostgreSQL"""
    return psycopg2.connect(**POSTGRES_CONFIG)