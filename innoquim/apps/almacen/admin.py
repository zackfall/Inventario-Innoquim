from django.contrib import admin
from .models import Almacen

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Almacén.
    Permite visualizar y gestionar las secciones del almacén en el panel de administración.
    """
    # Campos que se mostrarán en la lista de almacenes
    list_display = ('nombre', 'descripcion')
    
    # Campos en los que se puede buscar
    search_fields = ('nombre', 'descripcion')
    
    # Orden por defecto de visualización
    ordering = ('nombre',)
