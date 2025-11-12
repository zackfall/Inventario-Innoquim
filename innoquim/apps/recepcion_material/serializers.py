from rest_framework import serializers
from .models import RecepcionMaterial
from innoquim.apps.almacen.serializers import AlmacenSerializer

class RecepcionMaterialSerializer(serializers.ModelSerializer):
    almacen_detail = AlmacenSerializer(source='id_almacen', read_only=True)

    class Meta:
        model = RecepcionMaterial
        fields = ['id', 'fecha_recepcion', 'id_almacen', 'almacen_detail', 'observaciones']
        read_only_fields = ['fecha_recepcion']