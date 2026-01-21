from django.apps import AppConfig


class LoteProduccionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'innoquim.apps.lote_produccion'
    
    def ready(self):
        """Registrar signals al iniciar la app."""
        import innoquim.apps.lote_produccion.signals
