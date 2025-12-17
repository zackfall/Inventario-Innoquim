from django.contrib import admin
from .models import OrdenCliente
from innoquim.apps.orden_item.models import OrdenItem


class OrdenItemInline(admin.TabularInline):
    """
    Inline para gestionar items de orden dentro de OrdenCliente.
    """
    model = OrdenItem
    extra = 1  # Muestra 1 fila extra vacia para agregar items
    fields = ("product", "quantity", "subtotal", "created_at")
    readonly_fields = ("subtotal", "created_at")  # Campos calculados automaticamente
    can_delete = True


@admin.register(OrdenCliente)
class OrdenClienteAdmin(admin.ModelAdmin):
    """
    Configuracion del panel de administracion para OrdenCliente.
    """
    
    # Mostrar items inline en el formulario de orden
    inlines = [OrdenItemInline]
    
    # Columnas visibles en la lista
    list_display = [
        "order_code",
        "client",
        "order_date",
        "status",
        "total_display",
        "created_at"
    ]
    
    # Filtros laterales
    list_filter = ["status", "order_date"]
    
    # Campos por los que se puede buscar
    search_fields = ["order_code", "client__nombre_empresa", "client__nombre_contacto"]
    
    # Campos no editables
    readonly_fields = ["created_at", "updated_at", "tax_amount", "total_amount"]

    # Organizacion del formulario en secciones
    fieldsets = (
        ("Información de Orden", {
            "fields": ("client", "order_code", "order_date", "status", "tax_rate")
        }),
        ("Detalles", {
            "fields": ("notes",)
        }),
        ("Montos", {
            "fields": ("tax_amount", "total_amount")
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    # Metodo personalizado para mostrar el total formateado
    def total_display(self, obj):
        return obj.total_amount
    total_display.short_description = "Total"