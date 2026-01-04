from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["product_code", "name", "categoria_id", "unit", "weight", "price", "stock", "created_at"]
    
    list_filter = ["categoria_id", "unit", "created_at"]
    
    search_fields = ["product_code", "name", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Información General", {
            "fields": ("product_code", "name", "description", "categoria_id")
        }),
        ("Especificaciones", {
            "fields": ("unit", "weight", "price", "stock")
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"), 
            "classes": ("collapse",)
        }),
    )