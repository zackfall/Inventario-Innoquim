from django.contrib import admin
from .models import MateriaPrima


@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para MateriaPrima.
    """
    
    # Columnas visibles en la lista
    list_display = [
        'materia_prima_id',
        'codigo',
        'nombre',
        'unidad_id',
        'stock',
        'densidad',
    ]
    
    # Filtros laterales
    list_filter = ['unidad_id', 'fecha_creacion']
    
    # Campos por los que se puede buscar
    search_fields = ['materia_prima_id', 'codigo', 'nombre']
    
    # Campos no editables
    readonly_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']
    
    # Organizacion del formulario en secciones
    fieldsets = (
        ('Identificacion', {
            'fields': ('materia_prima_id', 'codigo')
        }),
        ('Informacion General', {
            'fields': ('nombre', 'descripcion', 'unidad_id')
        }),
        ('Propiedades', {
            'fields': ('densidad', 'stock')
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )