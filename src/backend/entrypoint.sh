#!/bin/bash
# Añadir el directorio actual al PYTHONPATH
export PYTHONPATH=/app

# Ejecutar la aplicación
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000