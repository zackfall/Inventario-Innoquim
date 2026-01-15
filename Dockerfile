# Usa una imagen oficial de Python 3.12 (según tus archivos .pyc)
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y permite logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para Postgres (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . /app/

# Colectar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Exponer el puerto de Django
EXPOSE 8000

# Comando para ejecutar la aplicación en producción
CMD python manage.py migrate && gunicorn innoquim.wsgi:application --bind 0.0.0.0:$PORT
