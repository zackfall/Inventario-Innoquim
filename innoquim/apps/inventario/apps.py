from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'innoquim.apps.innoquim.apps.inventario'
    verbose_name = 'Inventario y Kardex'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import innoquim.apps.inventario.signals
        pass