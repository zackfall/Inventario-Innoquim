from django.db import models
from decimal import Decimal


class MaterialProduccion(models.Model):
    """
    Tabla intermedia que relaciona un lote de producción con las materias primas utilizadas.
    
    Características:
    - Registra qué materias primas se usaron en cada lote
    - Cantidad en formato decimal para permitir fracciones (ej: 2.5 kg)
    - Guarda el costo unitario al momento de la producción para calcular costos reales
    """
    
    batch = models.ForeignKey(
        "lote_produccion.LoteProduccion",
        on_delete=models.CASCADE,
        related_name="materiales",
        verbose_name="Lote de Producción"
    )
    
    raw_material = models.ForeignKey(
        "materia_prima.MateriaPrima",
        on_delete=models.PROTECT,
        related_name="materiales_produccion",
        verbose_name="Materia Prima"
    )
    
    # CAMBIO IMPORTANTE: Usar DecimalField con más precisión
    used_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,  # Permite 0.0001 kg
        verbose_name="Cantidad Usada",
        help_text="Cantidad de materia prima utilizada en este lote"
    )
    
    unit = models.ForeignKey(
        "unidad.Unidad",
        on_delete=models.PROTECT,
        related_name="materiales_produccion",
        verbose_name="Unidad de Medida"
    )
    
    # NUEVO: Guardar el costo unitario al momento de usar el material
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name="Costo Unitario",
        help_text="Costo promedio de la materia prima al momento de usarla"
    )
    
    # NUEVO: Costo total del material en este lote
    costo_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Costo Total",
        help_text="used_quantity * costo_unitario"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "material_produccion"
        verbose_name = "Material de Producción"
        verbose_name_plural = "Materiales de Producción"
        ordering = ["-created_at"]
        
        # NUEVO: Evitar duplicados del mismo material en un lote
        unique_together = [['batch', 'raw_material']]

    def __str__(self):
        return f"Lote {self.batch.batch_code} - {self.raw_material.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Calcula el costo total antes de guardar.
        Obtiene el costo_promedio actual de la materia prima si no se especifica.
        """
        if not self.costo_unitario or self.costo_unitario == 0:
            self.costo_unitario = self.raw_material.costo_promedio
        
        self.costo_total = (self.used_quantity * self.costo_unitario).quantize(
            Decimal('0.01')
        )
        
        super().save(*args, **kwargs)