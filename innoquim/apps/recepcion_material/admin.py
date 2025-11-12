from django.contrib import admin
from .models import RecepcionMaterial

@admin.register(RecepcionMaterial)
class RecepcionMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_recepcion', 'id_almacen', 'observaciones')
    list_filter = ('id_almacen', 'fecha_recepcion')
    search_fields = ('observaciones', 'id_almacen__nombre')
    ordering = ('-fecha_recepcion',)
