#!/bin/bash
# Script para probar el failover automático

set -e

echo "🧪 Test de Failover Automático"
echo "================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Verificar health check
echo -e "${YELLOW}[Test 1]${NC} Verificando health check..."
HEALTH=$(curl -s http://localhost:8000/api/health/)
echo "$HEALTH" | jq .

if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo -e "${GREEN}✓ Sistema saludable${NC}"
else
    echo -e "${RED}✗ Sistema degradado o no saludable${NC}"
fi
echo ""

# Test 2: Conectividad a BD Principal
echo -e "${YELLOW}[Test 2]${NC} Verificando BD Principal (db:5432)..."
if docker exec db pg_isready -U postgres -d innoquim_db; then
    echo -e "${GREEN}✓ BD Principal conectada${NC}"
else
    echo -e "${RED}✗ BD Principal no disponible${NC}"
fi
echo ""

# Test 3: Conectividad a BD Replica
echo -e "${YELLOW}[Test 3]${NC} Verificando BD Replica (db-replica:5433)..."
if docker exec db-replica pg_isready -U postgres -d innoquim_db; then
    echo -e "${GREEN}✓ BD Replica conectada${NC}"
else
    echo -e "${RED}✗ BD Replica no disponible${NC}"
fi
echo ""

# Test 4: Estado de replicación
echo -e "${YELLOW}[Test 4]${NC} Verificando estado de replicación..."
echo "Estado de senders en Master:"
docker exec db psql -U postgres -d innoquim_db -c "\x" -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;" || echo "⚠️  No hay replicadores conectados (esto es normal en el primer inicio)"
echo ""

# Test 5: Datos sincronizados
echo -e "${YELLOW}[Test 5]${NC} Verificando sincronización de datos..."
PRIMARY_COUNT=$(docker exec db psql -U postgres -d innoquim_db -t -c "SELECT count(*) FROM usuario_usuario;" | xargs)
REPLICA_COUNT=$(docker exec db-replica psql -U postgres -d innoquim_db -t -c "SELECT count(*) FROM usuario_usuario;" | xargs)

echo "Usuarios en BD Principal: $PRIMARY_COUNT"
echo "Usuarios en BD Replica: $REPLICA_COUNT"

if [ "$PRIMARY_COUNT" == "$REPLICA_COUNT" ]; then
    echo -e "${GREEN}✓ Datos sincronizados${NC}"
else
    echo -e "${RED}✗ Datos desincronizados${NC}"
fi
echo ""

# Test 6: Simular fallo de BD Principal (opcional)
read -p "¿Deseas simular un fallo de BD Principal? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}[Test 6]${NC} Deteniendo BD Principal..."
    docker-compose stop db
    sleep 2
    
    echo -e "${YELLOW}[Test 6]${NC} Verificando failover..."
    HEALTH=$(curl -s http://localhost:8000/api/health/)
    echo "$HEALTH" | jq .
    
    if echo "$HEALTH" | jq -e '.databases.replica.status == "connected"' > /dev/null; then
        echo -e "${GREEN}✓ Failover a Replica exitoso${NC}"
    else
        echo -e "${RED}✗ Failover no funcionó${NC}"
    fi
    
    echo -e "${YELLOW}Restaurando BD Principal...${NC}"
    docker-compose start db
    sleep 5
    
    echo -e "${YELLOW}Verificando recuperación...${NC}"
    HEALTH=$(curl -s http://localhost:8000/api/health/)
    if echo "$HEALTH" | jq -e '.databases.primary.status == "connected"' > /dev/null; then
        echo -e "${GREEN}✓ BD Principal restaurada${NC}"
    else
        echo -e "${RED}✗ BD Principal no se recuperó${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Tests completados${NC}"
