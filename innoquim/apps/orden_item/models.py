from django.db import models


class OrdenItem(models.Model):
    order = models.ForeignKey(
        "orden_cliente.OrdenCliente", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "producto.Producto", on_delete=models.PROTECT, related_name="orden_items"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(
        "unidad.Unidad", on_delete=models.PROTECT, related_name="orden_items"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orden_item"
        verbose_name = "Orden Item"
        verbose_name_plural = "Orden Items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Item {self.id} - Order {self.order.id} - {self.product.name}"
