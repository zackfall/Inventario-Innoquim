# 📋 Resumen de Cambios - Sistema de Failover Automático

## 🎯 Objetivo
Implementar una **Base de Datos Espejo (Replica) con Failover Automático** para garantizar alta disponibilidad cuando la BD principal no esté disponible.

## 📁 Archivos Modificados

### 1. **docker-compose.yml** ✏️
- ✅ Agregado servicio `db-replica` con PostgreSQL 15
- ✅ Configurado replicación en streaming entre `db` (Master) y `db-replica` (Replica)
- ✅ Puerto de replica: `5433` (para acceso externo si es necesario)
- ✅ Volumen separado `postgres_replica_data` para datos de replica
- ✅ Health checks para ambas BDs

### 2. **innoquim/settings.py** ✏️
- ✅ Agregada configuración de múltiples bases de datos (default + replica)
- ✅ Agregado `DATABASE_ROUTERS` para enrutamiento inteligente
- ✅ Agregado middleware `HealthCheckMiddleware`
- ✅ Variables de entorno para `DATABASE_FAILOVER` y `DATABASE_REPLICA_URL`

### 3. **innoquim/db_failover.py** 🆕
- ✅ Clase `DatabaseFailoverRouter`: Maneja el cambio automático entre BD principal y replica
- ✅ Clase `HealthCheckMiddleware`: Monitorea la salud de las conexiones
- ✅ Lógica de lectura: Intenta principal → fallback a replica
- ✅ Lógica de escritura: Solo principal (error si no disponible)

### 4. **innoquim/apps/usuario/health_views.py** 🆕
- ✅ Endpoint `GET /api/health/` para monitorear el estado del sistema
- ✅ Verifica conectividad a BD principal, replica y Redis
- ✅ Retorna estado HTTP 200 (healthy) o 503 (degradado/unhealthy)

### 5. **innoquim/urls.py** ✏️
- ✅ Registrado endpoint de health check: `/api/health/`

### 6. **scripts/master_init.sh** 🆕
- ✅ Configura PostgreSQL como MASTER
- ✅ Crea usuario de replicación `replicator`
- ✅ Configura `pg_hba.conf` para permitir replicación

### 7. **scripts/replica_init.sh** 🆕
- ✅ Configura PostgreSQL como STANDBY/REPLICA
- ✅ Ejecuta `pg_basebackup` para clonar datos del master
- ✅ Configura `standby.signal` y `postgresql.auto.conf`

### 8. **.env.example** ✏️
- ✅ Agregadas nuevas variables de configuración:
  - `REPLICATION_USER` y `REPLICATION_PASSWORD`
  - `DATABASE_FAILOVER`
  - `DJANGO_SUPERUSER_*`

### 9. **DB_FAILOVER.md** 🆕
- ✅ Documentación completa del sistema de failover
- ✅ Instrucciones de configuración y monitoreo
- ✅ Ejemplos de troubleshooting

### 10. **test_failover.sh** 🆕
- ✅ Script interactivo para probar el failover automático
- ✅ Verifica replicación, sincronización y recuperación

## 🔧 Variables de Entorno Nuevas

Agregar a tu `.env`:

```bash
# Replicación
REPLICATION_USER=replicator
REPLICATION_PASSWORD=replication_password_123

# Failover
DATABASE_FAILOVER=true

# Superusuario
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@innoquim.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## 📊 Arquitectura del Failover

```
┌──────────────────────────────────────────┐
│          Django Backend                  │
├──────────────────────────────────────────┤
│    DatabaseFailoverRouter                │
│  - Intenta BD Principal (Read + Write)   │
│  - Si falla → Usa BD Replica (Read Only) │
├──────────────────────────────────────────┤
│                                          │
│  BD Principal         BD Replica         │
│  (Master)            (Standby)          │
│  Port 5432           Port 5433          │
│  ✓ Read/Write        ✓ Read Only        │
│                                          │
│  ◄─── Replication Streaming ────►       │
│  (Sincronización automática en tiempo   │
│   real de cambios)                       │
│                                          │
└──────────────────────────────────────────┘
```

## ✅ Cómo Usar

### 1. Iniciar el Sistema

```bash
cd /ruta/del/proyecto
docker-compose up --build
```

### 2. Verificar Health Check

```bash
curl http://localhost:8000/api/health/
```

### 3. Probar Failover

```bash
# Ejecutar script de prueba
bash test_failover.sh
```

### 4. Ver Logs de Replicación

```bash
docker-compose logs -f db | grep -i replication
docker-compose logs -f db-replica | grep -i standby
```

## 🛡️ Características de Seguridad

- ✅ Usuario de replicación con permisos limitados
- ✅ Contraseñas en `.env` (nunca en git)
- ✅ Comunicación dentro de red Docker aislada
- ✅ BD Replica es read-only (no escrituras accidentales)

## 📈 Monitoreo

**Endpoint disponible:**
- `GET /api/health/` - Estado del sistema en JSON

**Métricas que proporciona:**
- Status general del backend
- Conectividad a BD principal
- Conectividad a BD replica
- Estado de Redis
- Host de conexión de cada BD

## 🚀 Próximas Mejoras Opcionales

1. **Automatización de Failover con Patroni**: Para promover replica a master automáticamente
2. **pgBouncer**: Pool de conexiones para mayor eficiencia
3. **Monitoreo con Prometheus**: Métricas detalladas de replicación
4. **Backups Automáticos**: Snapshots periódicos de ambas BDs
5. **Alertas**: Notificaciones cuando ocurra un failover

## 📞 Soporte

Si hay problemas:

1. Revisar `DB_FAILOVER.md` - Sección Troubleshooting
2. Ver logs: `docker-compose logs -f`
3. Verificar conectividad: `docker ps` y `curl http://localhost:8000/api/health/`
4. Reiniciar sistema: `docker-compose down && docker-compose up --build`

---

**Implementado en:** January 17, 2026
**Sistema:** Docker Compose + PostgreSQL 15 + Django 5.2
