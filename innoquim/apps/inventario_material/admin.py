from django.contrib import admin
from .models import InventarioMaterial


@admin.register(InventarioMaterial)
class InventarioMaterialAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para InventarioMaterial.
    """
    
    # Columnas visibles en la lista
    list_display = [
        'inventario_material_id',
        'materia_prima_id',
        'almacen_id',
        'cantidad',
        'unidad_id',
        'fecha_actualizacion',
    ]
    
    # Filtros laterales para busqueda rapida
    list_filter = ['almacen_id', 'materia_prima_id', 'fecha_creacion']
    
    # Campos por los que se puede buscar
    search_fields = [
        'inventario_material_id',
        'materia_prima_id__nombre',
        'almacen_id__nombre',
    ]
    
    # Campos no editables en el formulario
    readonly_fields = ['inventario_material_id', 'fecha_creacion', 'fecha_actualizacion']
    
    # Organizacion del formulario en secciones
    fieldsets = (
        ('Identificacion', {
            'fields': ('inventario_material_id',)
        }),
        ('Ubicacion del Material', {
            'fields': ('materia_prima_id', 'almacen_id')
        }),
        ('Cantidad en Stock', {
            'fields': ('cantidad', 'unidad_id')
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )