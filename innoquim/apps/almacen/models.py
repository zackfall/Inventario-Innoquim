from django.db import models

# Modelo de Almacén que representa secciones de almacenamiento
class Almacen(models.Model):
    # Nombre de la sección del almacén
    nombre = models.CharField(max_length=100)
    
    # Descripción de la sección del almacén (ej: piso 1, pasillo A, etc.)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        """Retorna el nombre del almacén para representación en string"""
        return self.nombre