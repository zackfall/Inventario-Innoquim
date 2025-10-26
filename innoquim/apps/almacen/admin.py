from django.contrib import admin
from .models import Almacen

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion')
    search_fields = ('nombre', 'direccion')
    ordering = ('nombre',)
