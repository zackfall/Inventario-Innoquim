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
        'categoria_id',
        'unidad_id',
        'stock',
        'stock_minimo',
        'costo_promedio',
        'densidad',
    ]
    
    # Filtros laterales
    list_filter = ['categoria_id', 'unidad_id', 'fecha_creacion']
    
    search_fields = ['materia_prima_id', 'codigo', 'nombre']
    
    readonly_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']
    
    # Organización del formulario en secciones
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo',)
        }),
        ('Informacion General', {
            'fields': ('nombre', 'descripcion', 'categoria_id', 'unidad_id')
        }),
        ('Propiedades', {
            'fields': ('densidad',)
        }),
        ('Control de Stock', {
            'fields': ('stock', 'stock_minimo', 'stock_maximo', 'costo_promedio')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )