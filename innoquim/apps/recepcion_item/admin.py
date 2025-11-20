from django.contrib import admin
from .models import RecepcionItem

@admin.register(RecepcionItem)
class RecepcionItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_recepcion_material', 'cantidad', 'id_unidad', 'lote')
    list_filter = ('id_recepcion_material', 'id_unidad', 'lote')
    search_fields = ('lote', 'observaciones', 'id_recepcion_material__observaciones')
    ordering = ('-id_recepcion_material__fecha_recepcion', 'lote')
