from rest_framework import serializers
from .models import Almacen

class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ['id', 'nombre', 'direccion']