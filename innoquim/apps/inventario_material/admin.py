from django.contrib import admin
from .models import InventarioMaterial


@admin.register(InventarioMaterial)
class InventarioMaterialAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para InventarioMaterial (genérico).
    """

    # Columnas visibles en la lista
    list_display = [
        'inventario_material_id',
        'content_type',
        'object_id',
        'almacen_id',
        'cantidad',
        'unidad_id',
        'fecha_actualizacion',
    ]

    # Filtros laterales para busqueda rapida
    list_filter = ['almacen_id', 'content_type', 'fecha_creacion']

    # Campos por los que se puede buscar
    search_fields = [
        'inventario_material_id',
        'object_id',
        'almacen_id__nombre',
    ]

    # Campos no editables en el formulario
    readonly_fields = ['inventario_material_id', 'fecha_creacion', 'fecha_actualizacion']

    # Organizacion del formulario en secciones
    fieldsets = (
        ('Identificacion', {
            'fields': ('inventario_material_id',)
        }),
        ('Ítem y Ubicación', {
            'fields': ('content_type', 'object_id', 'almacen_id')
        }),
        ('Cantidad en Stock', {
            'fields': ('cantidad', 'unidad_id')
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )