-- Configuración del servidor master (principal)
-- Agregar esta configuración a postgresql.conf

# postgresql.conf (master)
max_wal_senders = 10
max_replication_slots = 10
wal_level = replica
wal_keep_size = 1GB

# pg_hba.conf (agregar esta línea para permitir replicación desde el replica)
# host    replication     all             db_replica      scram-sha-256
