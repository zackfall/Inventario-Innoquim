from django.db import models


class MaterialProduccion(models.Model):
    batch = models.ForeignKey(
        "lote_produccion.LoteProduccion",
        on_delete=models.CASCADE,
        related_name="materiales",
    )
    raw_material = models.ForeignKey(
        "materia_prima.MateriaPrima",
        on_delete=models.PROTECT,
        related_name="materiales_produccion",
    )
    used_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey(
        "unidad.Unidad", on_delete=models.PROTECT, related_name="materiales_produccion"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "material_produccion"
        verbose_name = "Material de Producción"
        verbose_name_plural = "Materiales de Producción"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Lote {self.batch.batch_code} - {self.raw_material.name}"
