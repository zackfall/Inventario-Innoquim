from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["product_code", "name", "unit", "weight", "created_at"]
    list_filter = ["unit", "created_at"]
    search_fields = ["product_code", "name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Información General", {"fields": ("product_code", "name", "description")}),
        ("Especificaciones", {"fields": ("unit", "weight")}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
