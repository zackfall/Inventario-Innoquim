from django.contrib import admin
from .models import Entrega

@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_entrega', 'estado', 'observaciones_cortas')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('estado', 'observaciones')
    ordering = ('-fecha_entrega',)
    
    def observaciones_cortas(self, obj):
        if obj.observaciones:
            return (obj.observaciones[:50] + '...') if len(obj.observaciones) > 50 else obj.observaciones
        return '-'
    observaciones_cortas.short_description = 'Observaciones'
