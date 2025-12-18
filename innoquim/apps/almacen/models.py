from django.db import models


# Create your models here.
class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class InventarioProducto(models.Model):
    producto = models.ForeignKey("producto.Producto", on_delete=models.PROTECT)
    almacen = models.ForeignKey("almacen.Almacen", on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # auto_now_add=True: se llena SOLO al crear el registro
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creacion"
    )

    # auto_now=True: se actualiza CADA VEZ que se modifica el registro
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Ultima Actualizacion"
    )

    class Meta:
        db_table = "inventario_producto"
        verbose_name = "Inventario de Producto"
        verbose_name_plural = "Inventario de Productos"
        unique_together = [["producto", "almacen"]]

