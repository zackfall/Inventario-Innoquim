from django.db import models
from ..recepcion_material.models import RecepcionMaterial
from ..materia_prima.models import MateriaPrima
from ..unidad.models import Unidad

# =================================================================
# MODELO RECEPCION ITEM
# =================================================================
class RecepcionItem(models.Model):
    """
    Modelo para gestionar items/detalles de las recepciones de material.
    
    Cada RecepcionItem representa un producto específico que fue recibido
    en una RecepcionMaterial (ej: 100kg de Acido Sulfurico en la recepción #1)
    
    Relaciones:
    - id_recepcion_material: FK a RecepcionMaterial (padre)
    - id_materia_prima: FK a MateriaPrima (qué se recibió)
    - id_unidad: FK a Unidad (cómo se mide)
    """
    
    # =================================================================
    # RELACIONES (FOREIGN KEYS)
    # =================================================================
    
    # id_recepcion_material: Referencia a la recepción padre
    # on_delete=CASCADE: si se elimina la recepción, se eliminan todos sus items
    # related_name: permite acceder desde RecepcionMaterial.items_recepcion
    id_recepcion_material = models.ForeignKey(
        RecepcionMaterial,
        on_delete=models.CASCADE,
        related_name='items_recepcion',
        verbose_name='Recepción Material',
        help_text='Referencia a la recepción principal a la que pertenece este item'
    )
    
    # id_materia_prima: Referencia a la materia prima recibida
    # on_delete=PROTECT: no permitir eliminar una materia prima si tiene recepciones asociadas
    # related_name: permite acceder desde MateriaPrima.items_recepcion
    id_materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.PROTECT,
        related_name='items_recepcion',
        verbose_name='Materia Prima',
        help_text='Material específico que fue recibido',
        null=True
    )
    
    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================
    
    # cantidad: cantidad recibida del material
    cantidad = models.IntegerField(
        verbose_name='Cantidad',
        help_text='Cantidad de unidades recibidas'
    )
    
    # id_unidad: unidad de medida (kg, litros, metros, etc)
    # on_delete=CASCADE: si se elimina la unidad, se eliminan los items que la usan
    id_unidad = models.ForeignKey(
        Unidad,
        on_delete=models.CASCADE,
        related_name='items_recepcion',
        verbose_name='Unidad de Medida',
        help_text='Unidad de medida utilizada para la cantidad'
    )
    
    # lote: número o código de lote del producto
    lote = models.CharField(
        max_length=100,
        verbose_name='Número de Lote',
        help_text='Identificador único del lote (ej: LOT-2025-001)'
    )
    
    # observaciones: notas adicionales sobre la recepción del item
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales, incidencias, o detalles especiales'
    )
    
    def __str__(self):
        """Representación legible del objeto"""
        return f"Item {self.id} - Lote: {self.lote} - Cantidad: {self.cantidad}"
        