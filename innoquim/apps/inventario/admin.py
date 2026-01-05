from django.contrib import admin
from .models import Kardex


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    """
    Panel de administración para Kardex (solo lectura).
    Los registros de Kardex NO deben modificarse manualmente.
    """

    list_display = [
        "fecha",
        "almacen",
        "get_item_display",
        "tipo_movimiento",
        "motivo",
        "cantidad",
        "costo_unitario",
        "saldo_cantidad",
        "saldo_costo_promedio",
    ]

    list_filter = [
        "tipo_movimiento",
        "motivo",
        "almacen",
        "fecha",
    ]

    search_fields = [
        "referencia_id",
        "observaciones",
    ]

    readonly_fields = [
        "fecha",
        "almacen",
        "content_type",
        "object_id",
        "tipo_movimiento",
        "motivo",
        "cantidad",
        "costo_unitario",
        "costo_total",
        "saldo_cantidad",
        "saldo_costo_total",
        "saldo_costo_promedio",
        "referencia_id",
        "observaciones",
        "usuario",
    ]

    ordering = ["-fecha", "-id"]

    def get_item_display(self, obj):
        """Muestra el item de forma legible"""
        if obj.item:
            return str(obj.item)
        return f"{obj.content_type.model} #{obj.object_id}"

    get_item_display.short_description = "Item"

    def has_add_permission(self, request):
        """Deshabilitar creación manual"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deshabilitar eliminación manual"""
        return False

    def has_change_permission(self, request, obj=None):
        """Deshabilitar edición manual"""
        return False
