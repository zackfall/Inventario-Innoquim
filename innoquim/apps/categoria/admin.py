from django.contrib import admin
from .models import Categoria



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo']
    list_filter = ['tipo', 'fecha_creacion']
    search_fields = ['categoria_id', 'nombre', 'tipo']
    readonly_fields = ['categoria_id', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Informacion General', {
            'fields': ('tipo', 'nombre', 'descripcion')
        }),
        ('Auditoria', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )