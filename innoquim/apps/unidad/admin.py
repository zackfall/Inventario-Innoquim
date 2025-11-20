from django.contrib import admin
from .models import Unidad


@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ["nombre", "simbolo", "factor_conversion", "created_at"]
    search_fields = ["nombre", "simbolo"]
    readonly_fields = ["created_at", "updated_at"]
