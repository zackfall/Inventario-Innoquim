# 🎯 Guía Rápida de Failover Automático

## 🚀 Inicio Rápido

```bash
# 1. Asegúrate de tener las variables en .env
cat .env | grep -E "REPLICATION|FAILOVER|SUPERUSER"

# 2. Inicia los servicios
docker-compose up --build

# 3. Espera a que se sincronicen (30-60 segundos)
docker-compose logs -f | grep -i "ready\|sync"

# 4. Verifica el estado
curl -s http://localhost:8000/api/health/ | jq .
```

## 📊 Estado del Sistema

### Health Check Response

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

## 🔄 Flujo de Failover

### Escenario 1: Sistema Normal ✅

```
Application Request
        ↓
Try Primary (db:5432)
        ↓
    ✓ Success
        ↓
Use Primary Database
(Read + Write allowed)
```

### Escenario 2: BD Principal Caída ⚠️

```
Application Request
        ↓
Try Primary (db:5432)
        ↓
    ✗ Timeout/Connection Error
        ↓
Try Replica (db-replica:5433)
        ↓
    ✓ Success
        ↓
Use Replica Database
(Read Only - no escrituras)
```

### Escenario 3: Recuperación 🔄

```
BD Principal vuelve online
        ↓
Next Application Request
        ↓
Try Primary (db:5432)
        ↓
    ✓ Success (está sincronizada)
        ↓
Cambio automático a Primary
(Replicación continúa)
```

## 📍 Ubicación de Componentes

```
Proyecto/
├── docker-compose.yml          ← Configuración de contenedores
├── Dockerfile                  ← Imagen del backend
├── innoquim/
│   ├── settings.py            ← Configuración Django (DB routers)
│   ├── db_failover.py         ← Lógica de failover ⭐
│   ├── urls.py                ← Endpoints (health check)
│   └── apps/usuario/
│       └── health_views.py    ← Endpoint /api/health/ ⭐
├── scripts/
│   ├── master_init.sh         ← Config PostgreSQL Master ⭐
│   └── replica_init.sh        ← Config PostgreSQL Replica ⭐
├── .env                        ← Variables de entorno
├── .env.example                ← Plantilla de .env
├── DB_FAILOVER.md             ← Documentación completa
├── FAILOVER_SETUP.md          ← Este archivo
└── test_failover.sh           ← Script de pruebas

⭐ = Nuevos archivos/cambios importantes
```

## 🧪 Pruebas Rápidas

### Test 1: Health Check

```bash
curl http://localhost:8000/api/health/ | jq .
```

Debe retornar `"status": "healthy"`

### Test 2: Verificar Replicación

```bash
# Ver estado de replicadores en master
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT client_addr, state FROM pg_stat_replication;"
```

### Test 3: Datos Sincronizados

```bash
# Contar registros en ambas BDs
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT COUNT(*) FROM usuario_usuario;"

docker exec db-replica psql -U postgres -d innoquim_db \
  -c "SELECT COUNT(*) FROM usuario_usuario;"
```

Deben ser **iguales**

### Test 4: Simular Fallo

```bash
# Detener BD Principal
docker-compose stop db

# Verificar que cambie a replica
curl http://localhost:8000/api/health/ | jq .databases.replica.status

# Debería mostrar "connected"

# Restaurar
docker-compose start db
```

## 🐛 Troubleshooting Rápido

| Problema | Comando de Diagnóstico |
|----------|----------------------|
| Replica no conecta | `docker exec db-replica pg_isready -h db -U postgres` |
| No hay replicación | `docker exec db psql -U postgres -c "SELECT * FROM pg_replication_slots;"` |
| Datos desincronizados | `docker-compose logs db-replica \| grep -i "sync\|lsn"` |
| Health check falla | `curl http://localhost:8000/api/health/` |
| Logs del failover | `docker-compose logs web \| grep -i "failover\|replica\|unavailable"` |

## 🔑 Variables Clave

En tu `.env`:

```bash
# 1. Database Failover
DATABASE_FAILOVER=true  # Debe ser "true"

# 2. Replicación
REPLICATION_USER=replicator
REPLICATION_PASSWORD=<contraseña_segura>

# 3. URLs de BD
# DATABASE_URL=postgres://USER:PASSWORD@db:5432/DB
# DATABASE_REPLICA_URL=postgres://USER:PASSWORD@db-replica:5433/DB

# 4. Debug
DEBUG=False  # En producción
```

## 🎓 Cómo Funciona Internamente

### 1. **Bootstrap (Primer Inicio)**

```
docker-compose up --build
    ↓
Master (db) se inicia
    ↓
Replica (db-replica) espera
    ↓
Master está listo
    ↓
Replica ejecuta pg_basebackup
    ↓
Copia todos los datos del Master
    ↓
Inicia streaming replication
```

### 2. **Operación Normal**

```
Cliente ↔ Django Backend
             ↓
        DatabaseFailoverRouter
             ↓
        ¿Master disponible?
        ✓ Sí → Usa Master
        ✗ No → Usa Replica
```

### 3. **Failover**

```
Master cae
    ↓
Siguiente request a Django
    ↓
DatabaseFailoverRouter
    intenta Master (falla)
    ↓
    intenta Replica (OK)
    ↓
Cambia a Replica automáticamente
    ↓
Logging: "Usando BD Replica"
```

## 📝 Logs Importantes

```bash
# Ver que dice Django sobre las BDs
docker-compose logs web | grep -i "database\|replica\|failover"

# Ver que dice PostgreSQL Master sobre replicación
docker-compose logs db | grep -i "replication\|wal\|sender"

# Ver que dice PostgreSQL Replica sobre sincronización
docker-compose logs db-replica | grep -i "standby\|recovery\|sync"
```

## ✨ Características Implementadas

| Característica | Estado | Detalles |
|---|---|---|
| Replicación de datos | ✅ | En tiempo real (streaming) |
| Failover automático | ✅ | Sin intervención manual |
| Health check | ✅ | Endpoint `/api/health/` |
| Sincronización | ✅ | Continua y automática |
| Recuperación | ✅ | Automática al volver master |
| Read-only replica | ✅ | No permite escrituras |
| Logging detallado | ✅ | Disponible en `docker-compose logs` |
| Persistencia | ✅ | Volúmenes separados para cada BD |

## 🚨 Limitaciones Actuales

- La replica es **read-only** (perfecto para reportes)
- No hay **promoción automática** de replica a master (requiere Patroni)
- Las **escrituras siempre necesitan la BD principal**
- Sin **automatic recovery** de master caído (se debe iniciar manualmente)

---

**Última actualización:** January 17, 2026
**Versión:** 1.0 - Beta
