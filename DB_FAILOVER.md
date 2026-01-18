# 🔄 Configuración de Base de Datos con Failover Automático

## 📋 Descripción

La arquitectura implementa **replicación de PostgreSQL con failover automático** para alta disponibilidad:

- **BD Principal (MASTER)**: `db` en puerto 5432
- **BD Espejo (REPLICA)**: `db-replica` en puerto 5433
- **Replicación**: En tiempo real mediante streaming replication
- **Failover**: Automático en caso de que la BD principal no esté disponible

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Compose                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌──────────────────────┐           │
│  │ Web Backend  │    │ Health Check Monitor │           │
│  │ (Django)     │───▶│  GET /api/health/    │           │
│  └──────┬───────┘    └──────────────────────┘           │
│         │                                                 │
│         │  Primary: db:5432                              │
│         │  Fallback: db-replica:5433                     │
│         │                                                 │
│  ┌──────▼──────────────────────────┐                    │
│  │    Database Failover Router      │                    │
│  │  (innoquim/db_failover.py)       │                    │
│  └──────┬──────────────────────────┘                    │
│         │                                                 │
│    ┌────┴───────────────────────┐                       │
│    │                            │                        │
│ ┌──▼─────────────┐    ┌────────▼──────────┐            │
│ │ PostgreSQL 15  │    │ PostgreSQL 15     │            │
│ │ MASTER         │───▶│ REPLICA/STANDBY   │            │
│ │ (Port 5432)    │    │ (Port 5433)       │            │
│ │ - WAL enabled  │    │ - Hot Standby     │            │
│ │ - Replication  │    │ - Read-only       │            │
│ └────────────────┘    └───────────────────┘            │
│                                                           │
│  Streaming Replication (Continuous sync)                │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## ⚙️ Configuración en `.env`

Agrega estas variables a tu archivo `.env`:

```bash
# BD Principals
NAME=innoquim_db
USER=postgres
PASSWORD=tucontraseña123
HOST=localhost
PORT=5432

# Replicación
REPLICATION_USER=replicator
REPLICATION_PASSWORD=replication_password_123

# Django
DEBUG=True
SECRET_KEY=tu-secret-key-aqui

# Failover
DATABASE_FAILOVER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@innoquim.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## 🚀 Iniciar el Sistema

### Primer inicio (construir imagen):

```bash
docker-compose up --build
```

### Inicios posteriores:

```bash
docker-compose up
```

### Detener:

```bash
docker-compose down
```

### Ver logs:

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f web

# Solo BD principal
docker-compose logs -f db

# Solo BD replica
docker-compose logs -f db-replica

# Solo Redis
docker-compose logs -f redis
```

## 📊 Monitoreo

### Health Check Endpoint

```bash
# Verificar estado del sistema
curl http://localhost:8000/api/health/
```

Respuesta:
```json
{
  "status": "healthy",
  "backend": "running",
  "databases": {
    "primary": {
      "status": "connected",
      "host": "db"
    },
    "replica": {
      "status": "connected",
      "host": "db-replica",
      "readonly": true
    }
  },
  "redis": "connected"
}
```

### Acceder a la BD Replica

```bash
# Desde el contenedor
docker exec -it db-replica psql -U postgres -d innoquim_db

# Desde la máquina host (si PostgreSQL está instalado)
psql -h localhost -p 5433 -U postgres -d innoquim_db
```

### Ver estado de replicación

```bash
docker exec -it db psql -U postgres -d innoquim_db -c "\x" -c "SELECT * FROM pg_stat_replication;"
```

## 🔄 Flujo de Failover

### Caso Normal (BD Principal activa):

```
Request from Backend
    ↓
Try: database = "default" (db:5432)
    ✓ Success
    ↓
Use Primary Database (READ + WRITE)
```

### Caso de Fallo (BD Principal no disponible):

```
Request from Backend
    ↓
Try: database = "default" (db:5432)
    ✗ Failed
    ↓
Try: database = "replica" (db-replica:5433)
    ✓ Success
    ↓
Use Replica Database (READ ONLY)
```

### Escrituras:

Las escrituras **siempre intentan ir a la BD principal**. Si la principal no está disponible, el backend lanzará un error (no escritura en replica).

## 📝 Logs Importantes

```bash
# Logs de failover
docker-compose logs web | grep -i "failover\|replica\|unavailable"

# Logs de replicación
docker-compose logs db | grep -i "replication\|wal\|sender"

# Logs de replica sincronizando
docker-compose logs db-replica | grep -i "standby\|recovery\|sync"
```

## 🛠️ Troubleshooting

### Problema: Replica no se conecta al Master

```bash
# Verificar conectividad
docker exec db-replica nc -zv db 5432

# Ver logs de replica
docker-compose logs db-replica
```

### Problema: Replicación lenta

```bash
# Ver tamaño del WAL
docker exec db du -sh /var/lib/postgresql/data/pg_wal

# Optimizar replicación en docker-compose.yml
# Aumentar: max_wal_senders, max_replication_slots
```

### Problema: Desincronización de datos

```bash
# Forzar re-sincronización
docker-compose down
docker volume rm inventario-innoquim_postgres_replica_data
docker-compose up
```

## 🔐 Seguridad

- El usuario de replicación (`replicator`) tiene **permisos limitados solo a replicación**
- La replica es **read-only** (no puede escribir)
- Las contraseñas se almacenan en `.env` (nunca en git)
- La comunicación entre contenedores es **dentro de la red Docker** (aislada)

## 📚 Recursos

- [PostgreSQL Replication Docs](https://www.postgresql.org/docs/15/warm-standby.html)
- [Django Database Routing](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/)
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)

## ✅ Checklist de Verificación

- [ ] Contenedores levantados: `docker ps`
- [ ] BD Principal conectada: `curl http://localhost:8000/api/health/`
- [ ] Replicación activa: `docker exec db psql -U postgres -c "SELECT * FROM pg_stat_replication;"`
- [ ] Datos en replica: `docker exec db-replica psql -U postgres -d innoquim_db -c "SELECT count(*) FROM ..."`
- [ ] Health check retorna healthy: `curl http://localhost:8000/api/health/ | jq .status`
