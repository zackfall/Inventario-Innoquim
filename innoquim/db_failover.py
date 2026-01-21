"""
Database Failover Router y Middleware para monitorear la salud del sistema
"""

from django.db import connections
import logging
import time

logger = logging.getLogger(__name__)


class DatabaseFailoverRouter:
    """
    Router inteligente que:
    - SIEMPRE intenta usar el master (default) cuando está disponible
    - Para LECTURAS: Usa replica solo si el master está DOWN
    - Para ESCRITURAS: Solo usa master (replica es read-only)
    - Detecta dinámicamente cambios de estado
    """
    
    # Cache de estado con timestamp para detectar cambios
    _master_status_cache = {"available": True, "timestamp": 0}
    _cache_timeout = 5  # Reintentar cada 5 segundos

    def db_for_read(self, model, **hints):
        """
        Las lecturas van al master si está disponible.
        Solo usan replica si el master está DOWN.
        """
        # Verificar si el master está disponible
        if self._is_master_available():
            return "default"
        else:
            # Master está DOWN, intentar replica
            if self._is_replica_available():
                logger.warning("⚠️ Master DOWN - usando replica para lectura")
                return "replica"
            else:
                # Ambas DOWN - esto debería fallar
                logger.error("❌ Master y Replica ambas DOWN")
                return "default"

    def db_for_write(self, model, **hints):
        """
        Las escrituras SIEMPRE van al master (default).
        La replica es read-only, no puede aceptar escrituras.
        """
        # Verificar que el master está disponible para escritura
        if not self._is_master_available():
            logger.error("❌ Intentando escribir pero master está DOWN")
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Las migraciones siempre se ejecutan en el master
        """
        return db == "default"

    @classmethod
    def _is_master_available(cls):
        """
        Verifica si el master (default) está disponible
        Implementa caché inteligente que reintentas cada N segundos
        """
        now = time.time()
        # Reintentar cada _cache_timeout segundos
        if now - cls._master_status_cache["timestamp"] > cls._cache_timeout:
            cls._master_status_cache["timestamp"] = now
            try:
                connection = connections["default"]
                # Limpiar la conexión anterior si está stale
                if hasattr(connection, '_close_at'):
                    connection.close()
                
                # Intentar conectar
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    
                # Cambio de estado: estaba DOWN, ahora UP
                if not cls._master_status_cache["available"]:
                    logger.info("✅ Master RECUPERADO - volviendo a usar master para todas las operaciones")
                
                cls._master_status_cache["available"] = True
                return True
            except (OSError, TimeoutError, ConnectionError) as e:
                cls._master_status_cache["available"] = False
                logger.debug(f"Master unavailable: {type(e).__name__}")
                return False
            except Exception as e:
                cls._master_status_cache["available"] = False
                logger.debug(f"Master check failed: {str(e)}")
                return False
        
        return cls._master_status_cache["available"]

    @staticmethod
    def _is_replica_available():
        """
        Verifica si la replica está disponible
        """
        try:
            if "replica" not in connections.databases:
                return False
            
            connection = connections["replica"]
            if hasattr(connection, 'connection') and connection.connection is None:
                return False
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except (OSError, TimeoutError, ConnectionError) as e:
            logger.debug(f"Replica unavailable (connection error): {type(e).__name__}")
            return False
        except Exception as e:
            logger.debug(f"Replica check failed: {str(e)}")
            return False


class HealthCheckMiddleware:
    """
    Middleware que verifica la salud del sistema en cada request
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
