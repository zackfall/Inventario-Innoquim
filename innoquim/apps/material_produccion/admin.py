from django.contrib import admin
from .models import MaterialProduccion


@admin.register(MaterialProduccion)
class MaterialProduccionAdmin(admin.ModelAdmin):
    list_display = [
        "batch",
        "raw_material",
        "used_quantity",
        "unit",
        "created_at"
    ]
    list_filter = ["batch__status", "raw_material", "created_at"]
    search_fields = ["batch__batch_code", "raw_material__name"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        (
            "Información del Material",
            {"fields": ("batch", "raw_material")},
        ),
        (
            "Cantidad Utilizada",
            {"fields": ("used_quantity", "unit")},
        ),
        (
            "Fechas",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
