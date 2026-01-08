from django.contrib import admin
from .models import Archivo


@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Archivo.
    """
    
    # Columnas visibles en la lista
    list_display = [
        'archivo_id',
        'nombre',
        'tipo_reporte',
        'tamaño_legible_display',
        'usuario_generador',
        'fecha_generacion',
    ]
    
    # Filtros laterales
    list_filter = [
        'tipo_reporte',
        'fecha_generacion',
        'usuario_generador',
    ]
    
    # Campos por los que se puede buscar
    search_fields = [
        'archivo_id',
        'nombre',
        'descripcion',
        'google_drive_id',
    ]
    
    # Campos no editables
    readonly_fields = [
        'archivo_id',
        'google_drive_id',
        'url_descarga',
        'tamaño',
        'tamaño_legible_display',
        'fecha_generacion',
        'fecha_actualizacion',
    ]
    
    # Organización del formulario en secciones
    fieldsets = (
        ('Identificación', {
            'fields': ('archivo_id', 'nombre', 'tipo_reporte')
        }),
        ('Google Drive', {
            'fields': ('google_drive_id', 'url_descarga'),
            'description': 'Información del archivo en Google Drive'
        }),
        ('Metadata', {
            'fields': ('tamaño', 'tamaño_legible_display', 'descripcion')
        }),
        ('Usuario y Auditoría', {
            'fields': ('usuario_generador', 'fecha_generacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Ordenamiento por defecto
    ordering = ['-fecha_generacion']
    
    # Número de items por página
    list_per_page = 25
    
    # Acciones personalizadas
    actions = ['descargar_seleccionados']
    
    def tamaño_legible_display(self, obj):
        """Muestra el tamaño en formato legible en el admin"""
        return obj.get_tamaño_legible()
    tamaño_legible_display.short_description = 'Tamaño'
    
    def descargar_seleccionados(self, request, queryset):
        """Acción para marcar archivos seleccionados (placeholder)"""
        count = queryset.count()
        self.message_user(
            request,
            f'{count} archivo(s) seleccionado(s). Usa la URL de descarga para obtenerlos.'
        )
    descargar_seleccionados.short_description = 'Ver URLs de descarga'
    
    def has_add_permission(self, request):
        """
        Deshabilita la creación desde el admin.
        Los archivos deben subirse via API.
        """
        return False