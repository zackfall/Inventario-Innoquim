from django.apps import AppConfig


class ClienteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name: debe coincidir con la ruta real de la app dentro del proyecto (revisar si es 'innaquim.apps.cliente' o similar)
    name = 'innoquim.apps.cliente'
    verbose_name = 'Clientes'