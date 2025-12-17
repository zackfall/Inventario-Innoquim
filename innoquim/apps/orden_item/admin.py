from django.contrib import admin
from .models import OrdenItem


class OrdenItemInline(admin.TabularInline):
    """
    Inline para gestionar items dentro de OrdenCliente.
    """

    model = OrdenItem
    extra = 1  # Muestra 1 fila extra vacia para agregar items
    fields = ("product", "quantity", "subtotal", "created_at")
    readonly_fields = (
        "unit",
        "subtotal",
        "created_at",
    )  # Campos calculados automaticamente
    can_delete = True


@admin.register(OrdenItem)
class OrdenItemAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para OrdenItem.
    """

    # Columnas visibles en la lista
    list_display = [
        "id",
        "order",
        "product",
        "quantity",
        "unit",
        "subtotal",
        "created_at",
    ]

    # Filtros laterales
    list_filter = ["order", "product"]

    # Campos por los que se puede buscar
    search_fields = ["order__order_code", "product__name"]

    # Campos no editables
    readonly_fields = ["created_at", "updated_at", "subtotal", "unit"]

