# backend/main.py
import uvicorn
from backend.config import FASTAPI_CONFIG
from backend.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=FASTAPI_CONFIG['host'],
        port=FASTAPI_CONFIG['port'],
        reload=False  # Force disable reload when running directly
    )