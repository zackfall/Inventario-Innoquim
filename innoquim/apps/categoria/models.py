from django.db import models

class Categoria(models.Model):
    TYPE_CHOICES = [
        ('PRODUCT', 'Producto'),
        ('RAW_MATERIAL', 'Materia Prima'),
    ]
    
    categoria_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        indexes = [
            models.Index(fields=['tipo'], name='idx_categoria_tipo'),     
            models.Index(fields=['nombre'], name='idx_categoria_nombre'),
        ]
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"