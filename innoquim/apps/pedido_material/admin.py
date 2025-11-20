from django.contrib import admin
from .models import PedidoMaterial


@admin.register(PedidoMaterial)
class PedidoMaterialAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para PedidoMaterial.
    """
    
    # Columnas visibles en la lista
    list_display = [
        'pedido_material_id',
        'proveedor_id',
        'fecha_pedido',
        'fecha_entrega_esperada',
        'usuario_registro',
        'fecha_creacion',
    ]
    
    # Filtros laterales
    list_filter = ['proveedor_id', 'fecha_pedido', 'usuario_registro']
    
    # Campos por los que se puede buscar
    search_fields = [
        'pedido_material_id',
        'numero_orden_compra',
        'proveedor_id__nombre_empresa',
        'usuario_registro__username',
    ]
    
    # Campos no editables
    readonly_fields = ['pedido_material_id', 'fecha_creacion', 'fecha_actualizacion']
    
    # Organizacion del formulario
    fieldsets = (
        ('Identificacion', {
            'fields': ('pedido_material_id', 'numero_orden_compra')
        }),
        ('Proveedor', {
            'fields': ('proveedor_id',)
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_entrega_esperada')
        }),
        ('Usuario', {
            'fields': ('usuario_registro',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )