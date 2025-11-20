from rest_framework import serializers
from .models import LoteProduccion


class LoteProduccionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    manager_name = serializers.CharField(
        source="production_manager.name", read_only=True
    )

    class Meta:
        model = LoteProduccion
        fields = [
            "id",
            "product",
            "product_name",
            "batch_code",
            "production_date",
            "produced_quantity",
            "unit",
            "unit_name",
            "status",
            "production_manager",
            "manager_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
