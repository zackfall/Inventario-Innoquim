# ===================================================================
# ETAPA 1: Base con Python
# ===================================================================
FROM python:3.12-slim as base

# Informacion del mantenedor
LABEL maintainer="Innoquim Team"
LABEL description="Servicio de gestion de archivos con Google Drive"

# Establecer directorio de trabajo
WORKDIR /app

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ===================================================================
# ETAPA 2: Instalar dependencias
# ===================================================================
FROM base as dependencies

# Copiar archivo de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# ===================================================================
# ETAPA 3: Aplicacion final
# ===================================================================
FROM base as application

# Copiar dependencias instaladas desde la etapa anterior
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copiar codigo de la aplicacion
COPY . .

# Crear directorio para archivos temporales
RUN mkdir -p temp_uploads

# Crear usuario no-root para mayor seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8001

# Healthcheck para verificar que el servicio esta funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Comando para ejecutar la aplicacion
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]