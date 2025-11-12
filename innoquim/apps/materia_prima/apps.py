from django.apps import AppConfig


class MateriaPrimaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # name: debe coincidir con la ruta completa de la app
    name = 'innoquim.apps.materia_prima'
    verbose_name = 'Materias Primas'