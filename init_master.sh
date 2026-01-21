#!/bin/bash
set -e

# Esperar a que PostgreSQL esté listo
until pg_isready -U postgres; do
  echo "Esperando a que PostgreSQL esté listo..."
  sleep 1
done

# Crear slot de replicación si no existe
psql -U postgres << EOF
SELECT * FROM pg_create_physical_replication_slot('standby_slot') WHERE NOT EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name = 'standby_slot');
EOF

echo "Replica configurada exitosamente"
