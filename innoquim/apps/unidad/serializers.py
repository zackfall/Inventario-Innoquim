from rest_framework import serializers
from .models import Unidad


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = [
            "id",
            "nombre",
            "simbolo",
            "factor_conversion",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
