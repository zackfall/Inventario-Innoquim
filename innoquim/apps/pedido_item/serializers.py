from rest_framework import serializers
from .models import PedidoItem


class PedidoItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PedidoItem
        fields = [
            'id',
            'id_unidad_medida',
            'cantidad_solicitada',
            'cantidad_recibida'
        ]
        
    def validate(self, data):
        """
        Validar que la cantidad recibida no sea mayor que la solicitada
        """
        if data.get('cantidad_recibida', 0) > data.get('cantidad_solicitada', 0):
            raise serializers.ValidationError(
                "La cantidad recibida no puede ser mayor que la cantidad solicitada"
            )
        return data