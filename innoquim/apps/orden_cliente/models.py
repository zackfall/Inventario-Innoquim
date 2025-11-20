from django.db import models


class OrdenCliente(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("confirmed", "Confirmada"),
        ("in_progress", "En Proceso"),
        ("completed", "Completada"),
        ("cancelled", "Cancelada"),
    )

    client = models.ForeignKey(
        "cliente.Cliente", on_delete=models.PROTECT, related_name="ordenes"
    )
    order_code = models.CharField(max_length=50, unique=True)
    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orden_cliente"
        verbose_name = "Orden de Cliente"
        verbose_name_plural = "Órdenes de Cliente"
        ordering = ["-order_date"]

    def __str__(self):
        return f"{self.order_code} - {self.client}"
