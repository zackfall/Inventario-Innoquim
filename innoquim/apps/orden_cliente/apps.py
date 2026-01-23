from django.apps import AppConfig


class OrdenClienteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name: debe coincidir con la ruta completa de la app
    name = 'innoquim.apps.orden_cliente'

    def ready(self):
        # Importar señales para que se registren
        import innoquim.apps.orden_cliente.signals
