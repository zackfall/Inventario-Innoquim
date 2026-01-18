"""
API de health check para monitorear la salud del sistema
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connections
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint para verificar la salud del backend y las BDs
    GET /api/health/
    """
    health_status = {
        "status": "healthy",
        "backend": "running",
        "databases": {},
        "redis": "unknown",
    }

    # Verificar BD Principal
    try:
        connection = connections["default"]
        # Ensure connection is open
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["databases"]["primary"] = {
            "status": "connected",
            "host": connection.settings_dict.get("HOST"),
        }
    except Exception as e:
        error_msg = str(e)
        # No loguear como error si es solo un problema de DNS al iniciar
        if "Name or service not known" in error_msg or "No address associated" in error_msg:
            logger.warning(f"⚠️ BD Principal no disponible (DNS): {error_msg}")
        else:
            logger.error(f"❌ BD Principal no disponible: {error_msg}")
        health_status["databases"]["primary"] = {
            "status": "disconnected",
            "error": error_msg,
        }
        health_status["status"] = "degraded"

    # Verificar BD Replica
    if "replica" in settings.DATABASES:
        try:
            connection = connections["replica"]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["databases"]["replica"] = {
                "status": "connected",
                "host": connection.settings_dict.get("HOST"),
                "readonly": True,
            }
        except Exception as e:
            health_status["databases"]["replica"] = {
                "status": "disconnected",
                "error": str(e),
            }
            if health_status["databases"]["primary"]["status"] == "disconnected":
                health_status["status"] = "unhealthy"
                logger.error(f"❌ BD Replica también no disponible: {str(e)}")

    # Verificar Redis
    try:
        import redis
        redis_location = settings.CACHES.get('default', {}).get('LOCATION', 'redis://redis:6379')
        if isinstance(redis_location, tuple):
            redis_url = f"redis://{redis_location[0]}:{redis_location[1]}"
        else:
            redis_url = redis_location if redis_location.startswith('redis') else f"redis://{redis_location}"
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = f"disconnected: {str(e)}"
        logger.warning(f"⚠️ Redis no disponible: {str(e)}")

    # Retornar con código de estado apropiado
    http_status = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return Response(health_status, status=http_status)
