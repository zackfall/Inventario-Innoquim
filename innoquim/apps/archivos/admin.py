# archivos/admin.py
"""
Configuración del panel de administración para Archivos.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Archivo


@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    """
    Panel de administración para gestionar archivos.
    """
    
    list_display = [
        'archivo_id',
        'nombre_corto',
        'tipo_reporte',
        'tamaño_formateado',
        'usuario_generador',
        'fecha_generacion',
        'ver_en_drive',
    ]
    
    list_filter = [
        'tipo_reporte',
        'fecha_generacion',
        'usuario_generador',
    ]
    
    search_fields = [
        'archivo_id',
        'nombre',
        'descripcion',
        'google_drive_id',
    ]
    
    readonly_fields = [
        'archivo_id',
        'google_drive_id',
        'url_descarga',
        'fecha_generacion',
        'fecha_actualizacion',
        'tamaño_formateado',
        'preview_drive',
    ]
    
    fieldsets = (
        ('Información del Archivo', {
            'fields': (
                'archivo_id',
                'nombre',
                'tipo_reporte',
                'descripcion',
            )
        }),
        ('Google Drive', {
            'fields': (
                'google_drive_id',
                'url_descarga',
                'preview_drive',
            )
        }),
        ('Metadatos', {
            'fields': (
                'tamaño',
                'tamaño_formateado',
                'usuario_generador',
            )
        }),
        ('Auditoría', {
            'fields': (
                'fecha_generacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-fecha_generacion']
    
    def nombre_corto(self, obj):
        """Muestra el nombre del archivo truncado."""
        if len(obj.nombre) > 40:
            return f"{obj.nombre[:37]}..."
        return obj.nombre
    nombre_corto.short_description = 'Nombre'
    
    def tamaño_formateado(self, obj):
        """Muestra el tamaño en formato legible."""
        return obj.get_tamaño_legible()
    tamaño_formateado.short_description = 'Tamaño'
    
    def ver_en_drive(self, obj):
        """Botón para ver el archivo en Google Drive."""
        if obj.url_descarga:
            return format_html(
                '<a href="{}" target="_blank" class="button">Ver en Drive</a>',
                obj.url_descarga
            )
        return '-'
    ver_en_drive.short_description = 'Acciones'
    
    def preview_drive(self, obj):
        """Muestra un preview del archivo de Google Drive."""
        if obj.url_descarga:
            usuario = getattr(obj.usuario_generador, 'name', obj.usuario_generador.username) if obj.usuario_generador else 'N/A'
            return format_html(
                '<a href="{}" target="_blank">Abrir en Google Drive</a><br>'
                '<small>ID: {}</small><br>'
                '<small>Subido por: {}</small>',
                obj.url_descarga,
                obj.google_drive_id,
                usuario
            )
        return '-'
    preview_drive.short_description = 'Vista Previa'
    
    def has_delete_permission(self, request, obj=None):
        """
        Solo permite eliminar a superusuarios.
        Los usuarios normales deben usar la API.
        """
        return request.user.is_superuser