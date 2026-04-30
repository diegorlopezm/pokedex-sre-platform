FROM python:3.11-slim

# ✅ WORKDIR específico para la app
WORKDIR /app/backend

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# ✅ PYTHONPATH específico para el backend
ENV PYTHONPATH=/app

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Comando de inicio
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "error", "--limit-max-requests", "10000"]