from django.contrib.contenttypes.models import ContentType
from django.db import models


class Kardex(models.Model):
    TIPO_OPERACION = (
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    )

    ORIGEN_CHOICES = (
        ("COMPRA", "Compra/Recepción"),
        ("PRODUCCION", "Producción"),
        ("VENTA", "Venta/Orden Cliente"),
        ("AJUSTE", "Ajuste de Inventario"),
    )

    fecha = models.DateTimeField(auto_now_add=True)
    almacen = models.ForeignKey("almacen.Almacen", on_delete=models.CASCADE)

    # Generic Foreign Key para que el Kardex sirva para MateriaPrima Y Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(
        max_length=8
    )  # Aquí irá el MP000001 o el código del producto
    item = GenericForeignKey("content_type", "object_id")

    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_OPERACION)
    motivo = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)

    # Costos (Fundamental para un Kardex real)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    # SALDOS (Lo que queda DESPUÉS del movimiento)
    saldo_cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_costo_total = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Kardex"
        verbose_name_plural = "Kardex"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.item} - {self.cantidad}"
