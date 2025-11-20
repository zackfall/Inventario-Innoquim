from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cliente.
    - read_only_fields: evita que cliente_id y campos de auditoría se envíen/modifiquen desde el API.
    - Usar este serializer en el ViewSet para mantener la coherencia de creación.
    """

    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['cliente_id', 'fecha_registro', 'fecha_actualizacion']