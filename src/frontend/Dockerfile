FROM nginx:alpine

# Copiar archivos estáticos del frontend
COPY . /usr/share/nginx/html/

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80 (Nginx)
EXPOSE 80

# Health check para Nginx (¡IMPORTANTE!)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1

# Nginx corre automáticamente al iniciar el contenedor (no necesita CMD)