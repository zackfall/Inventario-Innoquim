from rest_framework import serializers
from .models import OrdenItem


class OrdenItemSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo OrdenItem.
    Convierte objetos Python <-> JSON para la API REST.
    """

    # Campos adicionales de solo lectura para mostrar nombres relacionados
    # Evita hacer peticiones extra para obtener los nombres
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    # Validacion de quantity: minimo 1 envase
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrdenItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",  # Campo extra para lectura
            "quantity",
            "unit",
            "unit_name",  # Campo extra para lectura
            "subtotal",  # Calculado automaticamente
            "created_at",
            "updated_at",
        ]
        # Campos que NO se pueden modificar via API
        read_only_fields = ["created_at", "updated_at", "subtotal", "unit"]

