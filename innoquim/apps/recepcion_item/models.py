from django.db import models

from ..recepcion_material.models import RecepcionMaterial
from ..unidad.models import Unidad


# Create your models here.
class RecepcionItem(models.Model):
    id_recepcion_material = models.ForeignKey(
        RecepcionMaterial, on_delete=models.CASCADE, related_name="items_recepcion"
    )
    cantidad = models.IntegerField()
    id_unidad = models.ForeignKey(
        Unidad, on_delete=models.CASCADE, related_name="items_recepcion"
    )
    lote = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    materia_prima = models.ForeignKey(
        "materia_prima.MateriaPrima",
        on_delete=models.PROTECT,
        related_name="items_recepcion",
    )  # Añadimos esta relación explícita para saber QUÉ se recibió
    precio_compra = models.DecimalField(max_digits=12, decimal_places=4, default=0.00)

    def __str__(self):
        return f"Item {self.id} - Lote: {self.lote} - Cantidad: {self.cantidad}"

