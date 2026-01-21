#!/bin/bash
set -e

# Este script configura PostgreSQL como MASTER para replicación

echo "🔧 Configurando PostgreSQL MASTER..."

# Crear usuario de replicación si no existe
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE $POSTGRES_REPLICATION_USER WITH REPLICATION ENCRYPTED PASSWORD '$POSTGRES_REPLICATION_PASSWORD' LOGIN;
EOSQL

echo "✓ Usuario de replicación '$POSTGRES_REPLICATION_USER' creado"

# Configurar acceso para replicación en pg_hba.conf
if ! grep -q "host replication" /var/lib/postgresql/data/pg_hba.conf; then
    echo "host    replication     $POSTGRES_REPLICATION_USER     0.0.0.0/0     md5" >> /var/lib/postgresql/data/pg_hba.conf
    echo "✓ Regla de replicación agregada a pg_hba.conf"
fi

# Crear replication slot para la replica (si no existe)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT * FROM pg_create_physical_replication_slot('standby_slot', false);
EOSQL

echo "✓ Slot de replicación 'standby_slot' creado (o ya existe)"

echo "✓ MASTER configurado exitosamente"
