from django.contrib import admin
from .models import LoteProduccion


@admin.register(LoteProduccion)
class LoteProduccionAdmin(admin.ModelAdmin):
    list_display = [
        "batch_code",
        "product",
        "production_date",
        "produced_quantity",
        "status",
        "production_manager",
    ]
    list_filter = ["status", "production_date", "product"]
    search_fields = ["batch_code", "product__name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Información del Lote",
            {"fields": ("product", "batch_code", "production_date")},
        ),
        (
            "Producción",
            {"fields": ("produced_quantity", "unit", "status", "production_manager")},
        ),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
