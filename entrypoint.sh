#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté listo..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL está listo!"

echo "Ejecutando migraciones..."
python manage.py migrate materia_prima 0001
python manage.py migrate

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "Verificando superusuario..."
python manage.py shell -c "
from innoquim.apps.usuario.models import Usuario
import os

username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@innoquim.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not Usuario.objects.filter(username=username).exists():
    Usuario.objects.create_superuser(email=email, username=username, password=password)
    print(f'✓ Superusuario {username} creado exitosamente')
else:
    print(f'✓ Superusuario {username} ya existe')
"

echo "Iniciando servidor..."
exec "$@"
