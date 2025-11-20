from django.db import models
from django.conf import settings


class LoteProduccion(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("in_progress", "En Proceso"),
        ("completed", "Completado"),
        ("cancelled", "Cancelado"),
    )

    product = models.ForeignKey(
        "producto.Producto", on_delete=models.PROTECT, related_name="lotes_produccion"
    )
    batch_code = models.CharField(max_length=50, unique=True)
    production_date = models.DateField()
    produced_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(
        "unidad.Unidad", on_delete=models.PROTECT, related_name="lotes_produccion"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    production_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lotes_gestionados",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lote_produccion"
        verbose_name = "Lote de Producción"
        verbose_name_plural = "Lotes de Producción"
        ordering = ["-production_date"]

    def __str__(self):
        return f"{self.batch_code} - {self.product.name}"
