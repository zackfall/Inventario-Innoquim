-- Configuración del servidor replica (standby)
-- Este archivo se ejecuta automáticamente al iniciar el contenedor

-- Cambiar password del usuario replicador si es necesario
-- Crear slot de replicación
SELECT * FROM pg_create_physical_replication_slot('replication_slot_primary');

-- Mostrar información de slots creados
SELECT slot_name, slot_type, active FROM pg_replication_slots;
