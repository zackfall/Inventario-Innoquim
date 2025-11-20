from django.contrib import admin
from .models import PedidoItem

@admin.register(PedidoItem)
class PedidoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_unidad_medida', 'cantidad_solicitada', 'cantidad_recibida', 'porcentaje_recibido')
    list_filter = ('id_unidad_medida',)
    search_fields = ('id_unidad_medida__nombre',)
    ordering = ('id',)

    def porcentaje_recibido(self, obj):
        if obj.cantidad_solicitada == 0:
            return "0%"
        porcentaje = (obj.cantidad_recibida / obj.cantidad_solicitada) * 100
        return f"{porcentaje:.1f}%"
    porcentaje_recibido.short_description = "% Recibido"
