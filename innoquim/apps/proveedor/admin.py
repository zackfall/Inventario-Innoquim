from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Proveedores.
    Define cómo se visualizan y gestionan los proveedores en el admin de Django.
    """
    
    # Columnas visibles en la lista principal
    list_display = [
        'proveedor_id',
        'ruc',
        'nombre_empresa',
        'nombre_contacto',
        'telefono',
        'email',
        'tipo_producto',
    ]
    
    # Filtros laterales para búsqueda rápida
    list_filter = ['tipo_producto', 'fecha_registro']
    
    # Campos habilitados para búsqueda
    search_fields = [
        'proveedor_id',
        'ruc',
        'nombre_empresa',
        'nombre_contacto',
        'email',
        'telefono',
    ]
    
    # Campos de solo lectura (no editables)
    readonly_fields = ['proveedor_id', 'fecha_registro', 'fecha_actualizacion']
    
    # Organización de campos en secciones
    fieldsets = (
        ('Identificación', {
            'fields': ('proveedor_id', 'ruc')
        }),
        ('Información de la Empresa', {
            'fields': ('nombre_empresa', 'tipo_producto')
        }),
        ('Información de Contacto', {
            'fields': ('nombre_contacto', 'telefono', 'email', 'direccion')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',),  # Sección colapsable
        }),
    )