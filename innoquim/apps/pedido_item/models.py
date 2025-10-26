from django.db import models
from ..unidad.models import Unidad

# Create your models here.
class PedidoItem(models.Model):
    id_unidad_medida = models.ForeignKey(
        Unidad,
        on_delete=models.CASCADE,
        related_name='items_pedido'
    )    
    cantidad_solicitada = models.IntegerField()
    cantidad_recibida = models.IntegerField()