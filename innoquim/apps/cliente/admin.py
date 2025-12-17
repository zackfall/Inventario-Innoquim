from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    
    # list_display: columnas visibles en la lista para identificar rápidamente registros
    list_display = [
        'cliente_id',
        'ruc',
        'nombre_empresa',
        'nombre_contacto',
        'telefono',
        'email',
    ]
    
    # list_filter: filtros laterales para facilitar búsquedas por estado/fecha
    list_filter = ['fecha_registro']
    
    # search_fields: campos indexados para búsqueda rápida desde el admin
    search_fields = ['cliente_id', 'ruc', 'nombre_empresa', 'nombre_contacto', 'email', 'telefono']
    
    # readonly_fields: evitar edición de campos de auditoría desde el admin
    readonly_fields = ['cliente_id', 'fecha_registro', 'fecha_actualizacion']
    
    # fieldsets: organiza el formulario de creación/edición en secciones
    fieldsets = (
        ('Identificación', {
            'fields': ('ruc',)
        }),
        ('Información de la Empresa', {
            'fields': ('nombre_empresa',)
        }),
        ('Información de Contacto', {
            'fields': ('nombre_contacto', 'telefono', 'email', 'direccion')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',),  # Aparece colapsada
        }),
    )