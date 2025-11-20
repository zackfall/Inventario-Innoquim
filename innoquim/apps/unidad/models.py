from django.db import models


class Unidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    simbolo = models.CharField(max_length=10)
    factor_conversion = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Factor de conversión respecto a la unidad base",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "unidad"
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"
