from django.contrib import admin
from .models import RecepcionMaterial

@admin.register(RecepcionMaterial)
class RecepcionMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'materia_prima', 'cantidad', 'proveedor', 'fecha_de_recepcion', 'almacen', 'total')
    list_filter = ('almacen', 'fecha_de_recepcion', 'proveedor', 'materia_prima')
    search_fields = ('materia_prima__nombre', 'proveedor', 'numero_de_factura', 'observaciones')
    ordering = ('-fecha_de_recepcion',)
    readonly_fields = ('total', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('materia_prima', 'almacen', 'proveedor', 'fecha_de_recepcion')
        }),
        ('Detalles de Recepción', {
            'fields': ('cantidad', 'costo_unitario', 'total', 'numero_de_factura')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Información de Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
