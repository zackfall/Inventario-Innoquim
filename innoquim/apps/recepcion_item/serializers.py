from rest_framework import serializers
from .models import RecepcionItem
from innoquim.apps.recepcion_material.serializers import RecepcionMaterialSerializer


class RecepcionItemSerializer(serializers.ModelSerializer):
    recepcion_material_detail = RecepcionMaterialSerializer(source='id_recepcion_material', read_only=True)
    
    class Meta:
        model = RecepcionItem
        fields = [
            'id', 
            'id_recepcion_material', 
            'recepcion_material_detail',
            'cantidad', 
            'id_unidad',
            'lote', 
            'observaciones'
        ]