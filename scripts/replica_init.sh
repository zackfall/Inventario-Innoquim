#!/bin/bash
set -e

echo "🔧 Configurando PostgreSQL REPLICA..."

# Esperar a que el MASTER esté listo
echo "⏳ Esperando al MASTER (db)..."
until pg_isready -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
    sleep 2
done
echo "✓ MASTER está listo"

# Crear directorio de datos si no existe
mkdir -p /var/lib/postgresql/data
cd /var/lib/postgresql/data

# Si el directorio no está vacío, significa que es una re-inicialización
if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
    echo "📥 Clonando BD desde MASTER usando pg_basebackup..."
    
    pg_basebackup \
        --host=db \
        --username=$POSTGRES_REPLICATION_USER \
        --pgdata=/var/lib/postgresql/data \
        --progress \
        --write-recovery-conf \
        --wal-method=stream \
        --slot=standby_slot
    
    echo "✓ pg_basebackup completado"
else
    echo "✓ Los datos ya existen, saltando pg_basebackup"
fi

# Crear/actualizar standby.signal para indicar que es standby
touch /var/lib/postgresql/data/standby.signal

# Crear postgresql.auto.conf si no existe
if [ ! -f /var/lib/postgresql/data/postgresql.auto.conf ]; then
    cat > /var/lib/postgresql/data/postgresql.auto.conf <<EOF
# PostgreSQL STANDBY/REPLICA Configuration
recovery_target_timeline = 'latest'
restore_command = 'exit 1'
hot_standby = on
EOF
fi

echo "✓ REPLICA configurada exitosamente"
