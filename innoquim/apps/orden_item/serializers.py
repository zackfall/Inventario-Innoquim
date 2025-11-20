from rest_framework import serializers
from .models import OrdenItem


class OrdenItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = OrdenItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "quantity",
            "unit",
            "unit_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
