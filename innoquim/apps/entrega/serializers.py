from rest_framework import serializers
from .models import Entrega

class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = ['id', 'fecha_entrega', 'estado', 'observaciones']
        read_only_fields = ['fecha_entrega']
        
    def validate_estado(self, value):
        """
        Validar que el estado sea uno de los valores permitidos
        """
        estados_permitidos = ['pendiente', 'en_proceso', 'entregado', 'cancelado']
        if value.lower() not in estados_permitidos:
            raise serializers.ValidationError(
                f"Estado no válido. Los estados permitidos son: {', '.join(estados_permitidos)}"
            )
        return value.lower()