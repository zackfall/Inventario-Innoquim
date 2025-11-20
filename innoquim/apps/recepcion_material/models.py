from django.db import models
from innoquim.apps.almacen.models import Almacen

# Create your models here.
class RecepcionMaterial(models.Model):
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    id_almacen = models.ForeignKey(
        Almacen,
        on_delete=models.CASCADE,
        related_name='recepciones_material'
    )
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Recepción {self.id} - {self.fecha_recepcion.strftime('%Y-%m-%d %H:%M')}"
