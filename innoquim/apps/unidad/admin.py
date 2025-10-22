from django.contrib import admin
from .models import Unidad

# Register your models here.
@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'simbolo', 'factor_conversion')  # columnas visibles
    search_fields = ('nombre', 'simbolo')  # campo de búsqueda
    ordering = ('nombre',)  # orden por defecto