#!/bin/bash
# Comandos Rápidos de Referencia para el Sistema de Failover

# ═══════════════════════════════════════════════════════════════════════════
# 🚀 INICIAR SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

# Primer inicio (construir imagen)
docker-compose up --build

# Inicios posteriores
docker-compose up

# En background
docker-compose up -d

# ═══════════════════════════════════════════════════════════════════════════
# 🛑 DETENER SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

# Detener todos los servicios
docker-compose down

# Detener pero mantener volúmenes
docker-compose down -v  # ⚠️ CUIDADO: Borra datos!

# ═══════════════════════════════════════════════════════════════════════════
# 📊 MONITOREO Y HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

# Health check del sistema
curl http://localhost:8000/api/health/ | jq .

# Ver si está healthy (solo status)
curl -s http://localhost:8000/api/health/ | jq .status

# Ver estado de las BDs
curl -s http://localhost:8000/api/health/ | jq .databases

# ═══════════════════════════════════════════════════════════════════════════
# 📝 LOGS
# ═══════════════════════════════════════════════════════════════════════════

# Ver todos los logs
docker-compose logs

# Seguir logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Solo del backend
docker-compose logs -f web

# Solo de BD Principal
docker-compose logs -f db

# Solo de BD Replica
docker-compose logs -f db-replica

# Solo de Redis
docker-compose logs -f redis

# Buscar errores
docker-compose logs | grep ERROR

# Buscar eventos de replicación
docker-compose logs db | grep -i replication

# ═══════════════════════════════════════════════════════════════════════════
# 🔄 REPLICACIÓN - VERIFICAR ESTADO
# ═══════════════════════════════════════════════════════════════════════════

# Ver replicadores activos en master
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"

# Ver slots de replicación
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT * FROM pg_replication_slots;"

# Ver LSN (Log Sequence Number) - posición de replicación
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT now(), pg_current_xlog_location();"

# Ver tamaño del WAL
docker exec db du -sh /var/lib/postgresql/data/pg_wal/

# ═══════════════════════════════════════════════════════════════════════════
# 📦 VERIFICAR DATOS - SINCRONIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════

# Contar usuarios en master
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT COUNT(*) as usuarios_master FROM usuario_usuario;"

# Contar usuarios en replica
docker exec db-replica psql -U postgres -d innoquim_db \
  -c "SELECT COUNT(*) as usuarios_replica FROM usuario_usuario;"

# Ver todas las tablas y sus conteos
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT tablename, (SELECT COUNT(*) FROM pg_stat_user_tables WHERE relname = tablename) FROM pg_tables WHERE schemaname = 'public';"

# ═══════════════════════════════════════════════════════════════════════════
# 🧪 PRUEBAS DE FAILOVER
# ═══════════════════════════════════════════════════════════════════════════

# Ejecutar script de pruebas
bash test_failover.sh

# Simulación 1: Detener BD Principal
docker-compose stop db

# Verificar que cambió a replica
curl -s http://localhost:8000/api/health/ | jq '.databases.replica.status'

# Simulación 2: Restaurar BD Principal
docker-compose start db

# Verificar que volvió a principal
curl -s http://localhost:8000/api/health/ | jq '.databases.primary.status'

# ═══════════════════════════════════════════════════════════════════════════
# 🔌 CONEXIONES DE BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════════

# Acceder a BD Principal (dentro del contenedor)
docker exec -it db psql -U postgres -d innoquim_db

# Acceder a BD Replica (dentro del contenedor)
docker exec -it db-replica psql -U postgres -d innoquim_db

# Acceder desde máquina host (si PostgreSQL está instalado)
psql -h localhost -p 5432 -U postgres -d innoquim_db  # Master
psql -h localhost -p 5433 -U postgres -d innoquim_db  # Replica

# Ver conexiones activas
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity;"

# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ DJANGO SHELL
# ═══════════════════════════════════════════════════════════════════════════

# Entrar a Django shell
docker exec -it web python manage.py shell

# Dentro de Django shell:
# >>> from django.db import connections
# >>> connections['default']  # Ver conexión activa
# >>> from innoquim.apps.usuario.models import Usuario
# >>> Usuario.objects.all()  # Ver usuarios

# ═══════════════════════════════════════════════════════════════════════════
# 🧹 LIMPIEZA Y RESET
# ═══════════════════════════════════════════════════════════════════════════

# Detener todos y eliminar volúmenes (⚠️ BORRA DATOS)
docker-compose down -v

# Limpiar contenedores parados
docker container prune -f

# Limpiar volúmenes no usados
docker volume prune -f

# Reset total (⚠️ DESTRUYE TODO)
docker-compose down -v && docker-compose up --build

# ═══════════════════════════════════════════════════════════════════════════
# 📋 ESTADO DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

# Ver contenedores activos
docker ps

# Ver todos los contenedores (incluso parados)
docker ps -a

# Ver volúmenes
docker volume ls

# Ver redes
docker network ls

# Ver detalles de un contenedor
docker inspect db
docker inspect db-replica

# ═══════════════════════════════════════════════════════════════════════════
# 🔐 VARIABLES DE ENTORNO
# ═══════════════════════════════════════════════════════════════════════════

# Ver variables de entorno en archivo .env
cat .env

# Ver solo variables de replicación
cat .env | grep -i replication

# Ver solo variables de failover
cat .env | grep -i failover

# Verificar que .env tiene lo necesario
grep -E "REPLICATION_USER|REPLICATION_PASSWORD|DATABASE_FAILOVER" .env

# ═══════════════════════════════════════════════════════════════════════════
# 🚨 TROUBLESHOOTING COMÚN
# ═══════════════════════════════════════════════════════════════════════════

# Error: Red ya existe
docker network rm inventario-innoquim_innoquim_network
docker-compose up --build

# Replica no conecta
docker exec db-replica nc -zv db 5432

# Ver error específico en logs
docker-compose logs web | grep ERROR | head -20

# Reiniciar solo un servicio
docker-compose restart db
docker-compose restart db-replica
docker-compose restart web

# Reconstruir solo la imagen del backend
docker-compose build --no-cache web
docker-compose up web

# ═══════════════════════════════════════════════════════════════════════════
# 📚 DOCUMENTACIÓN RÁPIDA
# ═══════════════════════════════════════════════════════════════════════════

# Ver documentación principal
cat DB_FAILOVER.md

# Ver guía de setup
cat FAILOVER_SETUP.md

# Ver referencia rápida
cat QUICKSTART_FAILOVER.md

# Ver implementación
cat IMPLEMENTACION_COMPLETADA.md

# ═══════════════════════════════════════════════════════════════════════════
# 🎯 FLUJO TÍPICO DE TRABAJO
# ═══════════════════════════════════════════════════════════════════════════

# 1. Iniciar sistema
docker-compose up -d

# 2. Esperar a que se sincronice (30-60 segundos)
sleep 30

# 3. Verificar health
curl http://localhost:8000/api/health/ | jq .

# 4. Verificar replicación
docker exec db psql -U postgres -d innoquim_db \
  -c "SELECT COUNT(*) FROM pg_stat_replication;"

# 5. Si todo OK, el sistema está listo
echo "✅ Sistema listo para usar"

# ═══════════════════════════════════════════════════════════════════════════

echo "💡 Tip: Usa 'docker-compose logs -f' para ver logs en tiempo real"
echo "💡 Tip: Usa 'curl http://localhost:8000/api/health/' para verificar estado"
echo "💡 Tip: Lee DB_FAILOVER.md para documentación completa"
