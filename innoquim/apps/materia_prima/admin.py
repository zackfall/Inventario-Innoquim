from django.contrib import admin
from .models import MateriaPrima


@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para MateriaPrima.
    """
    
    list_display = [
        'materia_prima_id',
        'codigo',
        'nombre',
        'categoria_id',
        'unidad_id',
        'stock',
        'densidad',
    ]
    
    list_filter = ['categoria_id', 'unidad_id', 'fecha_creacion']
    
    search_fields = ['materia_prima_id', 'codigo', 'nombre']
    
    readonly_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Identificacion', {
            'fields': ('materia_prima_id', 'codigo')
        }),
        ('Informacion General', {
            'fields': ('nombre', 'descripcion', 'categoria_id', 'unidad_id')
        }),
        ('Propiedades', {
            'fields': ('densidad', 'stock')
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )