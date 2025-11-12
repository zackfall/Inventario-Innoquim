from django.contrib import admin
from .models import RecepcionItem

# =================================================================
# ADMIN RECEPCION ITEM
# =================================================================
@admin.register(RecepcionItem)
class RecepcionItemAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo RecepcionItem.
    Permite gestionar los items de recepción desde el panel administrativo.
    """
    
    # Campos a mostrar en la lista
    list_display = (
        'id',
        'id_recepcion_material',
        'id_materia_prima',
        'cantidad',
        'id_unidad',
        'lote'
    )
    
    # Campos que se pueden usar para filtrar
    list_filter = (
        'id_recepcion_material',
        'id_materia_prima',
        'id_unidad',
        'lote'
    )
    
    # Campos donde se puede hacer búsqueda
    search_fields = (
        'lote',
        'observaciones',
        'id_recepcion_material__observaciones',
        'id_materia_prima__nombre',
        'id_materia_prima__codigo'
    )
    
    # Ordenamiento por defecto
    ordering = (
        '-id_recepcion_material__fecha_recepcion',
        'lote'
    )
    
    # Agrupar campos relacionados en el formulario
    fieldsets = (
        ('Información de Recepción', {
            'fields': ('id_recepcion_material',)
        }),
        ('Material Recibido', {
            'fields': ('id_materia_prima',)
        }),
        ('Cantidad y Unidad', {
            'fields': ('cantidad', 'id_unidad')
        }),
        ('Datos de Lote', {
            'fields': ('lote',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)  # Permite contraer/expandir esta sección
        }),
    )
