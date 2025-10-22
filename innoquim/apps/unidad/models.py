from django.db import models

# Create your models here.
class Unidad(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    simbolo = models.CharField(max_length=10, unique=True)
    factor_conversion = models.FloatField(
        help_text="Factor de conversión respecto a la unidad base (por ejemplo, 1 g = 1.0, 1 kg = 1000.0)"
    )

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"