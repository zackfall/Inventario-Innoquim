from django.db import models

# Create your models here.
class Entrega(models.Model):
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Entrega {self.id} - {self.fecha_entrega.strftime('%Y-%m-%d %H:%M')}"