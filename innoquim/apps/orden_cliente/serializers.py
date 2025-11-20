from rest_framework import serializers
from .models import OrdenCliente


class OrdenClienteSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = OrdenCliente
        fields = [
            "id",
            "client",
            "client_name",
            "order_code",
            "order_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
