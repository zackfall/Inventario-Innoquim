from django.db import models
from innoquim.apps.almacen.models import Almacen
from innoquim.apps.materia_prima.models import MateriaPrima

# Create your models here.
class RecepcionMaterial(models.Model):
    # Campo para especificar la materia prima principal de esta recepción
    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.PROTECT,
        related_name='recepciones_principales',
        help_text="Materia prima principal de esta recepción",
        null=True,
        blank=True
    )
    
    # Cantidad total recibida (puede ser la suma de los items si hay múltiples)
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Cantidad total recibida",
        null=True,
        blank=True
    )
    
    # Costo unitario de la materia prima
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text="Costo unitario por unidad de materia prima",
        null=True,
        blank=True
    )
    
    # Total calculado (cantidad * costo_unitario)
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Total de la recepción (cantidad × costo_unitario)",
        null=True,
        blank=True
    )
    
    # Proveedor de la materia prima
    proveedor = models.CharField(
        max_length=200,
        help_text="Nombre del proveedor",
        null=True,
        blank=True
    )
    
    # Almacen donde se recibe el material
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='recepciones_material',
        null=True,
        blank=True
    )
    
    # Fecha de recepción (manual, no automática)
    fecha_de_recepcion = models.DateField(
        help_text="Fecha en que se recibió el material",
        null=True,
        blank=True
    )
    
    # Número de factura
    numero_de_factura = models.CharField(
        max_length=100,
        help_text="Número de factura del proveedor",
        null=True,
        blank=True
    )
    
    # Observaciones generales de la recepción
    observaciones = models.TextField(
        blank=True, 
        null=True,
        help_text="Observaciones generales de la recepción"
    )
    
    # Fecha de creación automática
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "recepcion_material"
        verbose_name = "Recepción de Material"
        verbose_name_plural = "Recepciones de Material"
        ordering = ["-fecha_de_recepcion"]
        
        indexes = [
            models.Index(fields=["materia_prima"]),
            models.Index(fields=["proveedor"]),
            models.Index(fields=["numero_de_factura"]),
            models.Index(fields=["-fecha_de_recepcion"]),
        ]
    
    def __str__(self):
        return f"Recepción {self.id} - {self.materia_prima.nombre} ({self.fecha_de_recepcion})"
    
    def save(self, *args, **kwargs):
        """Calcular automáticamente el total antes de guardar"""
        if self.cantidad and self.costo_unitario:
            self.total = self.cantidad * self.costo_unitario
        super().save(*args, **kwargs)
