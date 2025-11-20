from django.apps import AppConfig


class InventarioMaterialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name: debe coincidir con la ruta completa de la app
    name = 'innoquim.apps.inventario_material'
    verbose_name = 'Inventario de Materiales'
