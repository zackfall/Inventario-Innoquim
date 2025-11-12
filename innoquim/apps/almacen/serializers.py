from rest_framework import serializers
from .models import Almacen

class AlmacenSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Almacén.
    Convierte los datos del modelo a formato JSON y viceversa.
    """
    class Meta:
        model = Almacen
        # Campos que se van a exponer en la API
        fields = ['id', 'nombre', 'descripcion']