# Manual de Implementación - Sistema de Inventario Innoquim

## Tabla de Contenidos
1. [Arquitectura General](#arquitectura-general)
2. [Requisitos Previos](#requisitos-previos)
3. [Configuración del Backend (Django)](#configuración-del-backend-django)
4. [Configuración del Frontend (Vue.js)](#configuración-del-frontend-vuejs)
5. [Configuración de PostgreSQL](#configuración-de-postgresql)
6. [Configuración de Redis](#configuración-de-redis)
7. [Configuración de Nginx](#configuración-de-nginx)
8. [Despliegue en Máquina Virtual](#despliegue-en-máquina-virtual)
9. [Configuración del File Manager](#configuración-del-file-manager)
10. [Mantenimiento y Monitoreo](#mantenimiento-y-monitoreo)

---

## Arquitectura General

El sistema Innoquim consiste en:

- **Backend**: Django REST Framework con PostgreSQL
- **Frontend**: Vue.js 3 + Vite (desplegado como archivos estáticos)
- **Base de Datos**: PostgreSQL con réplica opcional
- **Caché**: Redis
- **Proxy**: Nginx
- **File Manager**: FastAPI para gestión de archivos en Google Drive

---

## Requisitos Previos

### Sistema Operativo
- Ubuntu 20.04+ o Debian 10+
- Mínimo 4GB RAM, 2 CPU cores
- 50GB espacio en disco

### Software Base
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib redis-server git curl wget
```

---

## Configuración del Backend (Django)

### 1. Clonar Repositorio
```bash
cd /home
sudo mkdir backend
sudo chown $USER:$USER backend
cd backend
git clone <URL_DEL_REPOSITORIO> Inventario-Innoquim
cd Inventario-Innoquim
```

### 2. Entorno Virtual Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Variables de Entorno
```bash
cp .env.example .env
nano .env
```

Configurar las siguientes variables:
```env
# Seguridad
SECRET_KEY="tu-clave-secreta-generada-con-python"
DEBUG=False  # IMPORTANTE: False en producción

# Base de Datos
NAME="innoquim_db"
USER="postgres"
PASSWORD="tu_contraseña_bd"
HOST="localhost"
PORT="5432"

# Redis
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_DB="0"

# Hosts permitidos
ALLOWED_HOSTS="localhost,127.0.0.1,tu-dominio.com,IP_DEL_SERVIDOR"

# Google Drive (opcional)
GOOGLE_DRIVE_FOLDER_ID="tu_folder_id"

# File Manager
FILE_MANAGER_URL="http://localhost:8001"
```

### 4. Configuración de Base de Datos
```bash
# Crear base de datos
sudo -u postgres createdb innoquim_db

# Crear usuario (opcional)
sudo -u postgres psql -c "CREATE USER innoquim_user WITH PASSWORD 'tu_contraseña';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE innoquim_db TO innoquim_user;"
```

### 5. Migraciones y Archivos Estáticos
```bash
# Activar entorno virtual
source venv/bin/activate

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput
```

### 6. Configurar Gunicorn
```bash
# Crear archivo de configuración de Gunicorn
sudo nano /etc/systemd/system/innoquim.service
```

Contenido del servicio:
```ini
[Unit]
Description=Innoquim Django Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/backend/Inventario-Innoquim
Environment="PATH=/home/backend/Inventario-Innoquim/venv/bin"
ExecStart=/home/backend/Inventario-Innoquim/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/backend/Inventario-Innoquim/innoquim.sock \
    innoquim.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Iniciar y habilitar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl start innoquim
sudo systemctl enable innoquim
```

---

## Configuración del Frontend (Vue.js)

### 1. Clonar y Construir Frontend
```bash
cd /home
sudo mkdir frontend
sudo chown $USER:$USER frontend
cd frontend
git clone <URL_DEL_REPOSITORIO_FRONTEND> inventario-frontend
cd inventario-frontend
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
nano .env
```

Configurar:
```env
# Apuntar al backend desplegado
VITE_API_URL=http://tu-dominio.com/api/
VITE_API_TIMEOUT=10000
```

### 3. Instalar Dependencias y Construir
```bash
# Instalar Node.js si no está actualizado
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar dependencias
npm install

# Construir para producción
npm run build
```

### 4. Copiar Archivos Estáticos a Nginx
```bash
sudo mkdir -p /var/www/innoquim
sudo cp -r dist/* /var/www/innoquim/
sudo chown -R www-data:www-data /var/www/innoquim
```

---

## Configuración de PostgreSQL

### 1. Configurar PostgreSQL
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Modificar:
```conf
# Conexiones
listen_addresses = 'localhost'
port = 5432

# Performance
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. Configurar Acceso
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Añadir:
```conf
local   all             postgres                                md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

Reiniciar PostgreSQL:
```bash
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

---

## Configuración de Redis

### 1. Configurar Redis
```bash
sudo nano /etc/redis/redis.conf
```

Configuraciones importantes:
```conf
# Seguridad
bind 127.0.0.1
port 6379
requirepass tu_contraseña_redis

# Persistencia
save 900 1
save 300 10
save 60 10000

# Memoria
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 2. Iniciar y Habilitar Redis
```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

---

## Configuración de Nginx

### 1. Crear Configuración de Nginx
```bash
sudo nano /etc/nginx/sites-available/innoquim
```

Contenido completo:
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com IP_DEL_SERVIDOR;
    
    # Frontend (Vue.js estático)
    location / {
        root /var/www/innoquim;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache para archivos estáticos
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend Django API
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/home/backend/Inventario-Innoquim/innoquim.sock;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Admin de Django
    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/home/backend/Inventario-Innoquim/innoquim.sock;
    }
    
    # Archivos estáticos de Django
    location /static/ {
        alias /home/backend/Inventario-Innoquim/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Archivos multimedia
    location /media/ {
        alias /home/backend/Inventario-Innoquim/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # File Manager (FastAPI)
    location /files/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Seguridad
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

### 2. Habilitar Sitio
```bash
sudo ln -s /etc/nginx/sites-available/innoquim /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Configuración del File Manager (Opcional)

### 1. Instalar Python Environment para File Manager
```bash
cd /home/backend/Inventario-Innoquim/file-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
nano .env
```

### 3. Crear Servicio Systemd
```bash
sudo nano /etc/systemd/system/innoquim-file-manager.service
```

Contenido:
```ini
[Unit]
Description=Innoquim File Manager Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/backend/Inventario-Innoquim/file-manager
Environment="PATH=/home/backend/Inventario-Innoquim/file-manager/venv/bin"
ExecStart=/home/backend/Inventario-Innoquim/file-manager/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Iniciar Servicio
```bash
sudo systemctl daemon-reload
sudo systemctl start innoquim-file-manager
sudo systemctl enable innoquim-file-manager
```

---

## Despliegue en Máquina Virtual

### 1. Configurar Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Configurar SSL con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

### 3. Configurar Renovación Automática
```bash
sudo crontab -e
```

Añadir:
```crontab
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Mantenimiento y Monitoreo

### 1. Logs del Sistema
```bash
# Backend Django
sudo journalctl -u innoquim -f

# File Manager
sudo journalctl -u innoquim-file-manager -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 2. Backups Automáticos
```bash
# Script de backup
sudo nano /home/backend/scripts/backup.sh
```

Contenido:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/backups"
DB_NAME="innoquim_db"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

Hacer ejecutable y programar:
```bash
chmod +x /home/backend/scripts/backup.sh
sudo crontab -e
```

Añadir:
```crontab
0 2 * * * /home/backend/scripts/backup.sh
```

### 3. Monitoreo Básico
```bash
# Script de monitoreo
sudo nano /home/backend/scripts/monitor.sh
```

Contenido:
```bash
#!/bin/bash

# Verificar servicios
services=("innoquim" "innoquim-file-manager" "nginx" "postgresql" "redis")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service está activo"
    else
        echo "✗ $service está inactivo"
        # Enviar notificación (opcional)
    fi
done
```

---

## Verificación Final

### 1. Verificar Funcionamiento
```bash
# Verificar servicios
sudo systemctl status innoquim
sudo systemctl status innoquim-file-manager
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Verificar API
curl -I http://localhost/api/

# Verificar frontend
curl -I http://localhost/
```

### 2. Test de Carga (Opcional)
```bash
# Instalar Apache Bench
sudo apt install apache2-utils

# Test básico
ab -n 100 -c 10 http://localhost/
```

---

## Troubleshooting Común

### 1. Problemas con Permisos
```bash
sudo chown -R www-data:www-data /home/backend/Inventario-Innoquim
sudo chmod -R 755 /home/backend/Inventario-Innoquim
sudo chown -R www-data:www-data /var/www/innoquim
```

### 2. Problemas con Base de Datos
```bash
# Verificar conexión
psql -h localhost -U postgres -d innoquim_db -c "SELECT version();"

# Verificar logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 3. Problemas con Nginx
```bash
# Test de configuración
sudo nginx -t

# Verificar logs
sudo tail -f /var/log/nginx/error.log
```

---

## Contacto y Soporte

Para cualquier problema durante la implementación:
1. Revisar logs del sistema
2. Verificar configuración de variables de entorno
3. Validar conectividad entre servicios
4. Consultar documentación oficial de Django, Vue.js y Nginx

---

*Última actualización: $(date)*