from django.contrib import admin
from .models import OrdenCliente


@admin.register(OrdenCliente)
class OrdenClienteAdmin(admin.ModelAdmin):
    list_display = ["order_code", "client", "order_date", "status", "created_at"]
    list_filter = ["status", "order_date"]
    search_fields = ["order_code", "client__name"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Información de Orden",
            {"fields": ("client", "order_code", "order_date", "status")},
        ),
        ("Detalles", {"fields": ("notes",)}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
