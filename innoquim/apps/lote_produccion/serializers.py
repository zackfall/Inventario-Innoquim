from rest_framework import serializers
from .models import LoteProduccion
from innoquim.apps.material_produccion.serializers import MaterialProduccionSerializer


class LoteProduccionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_code = serializers.CharField(source="product.product_code", read_only=True)
    unit_name = serializers.CharField(source="unit.nombre", read_only=True)
    unit_symbol = serializers.CharField(source="unit.simbolo", read_only=True)
    production_manager_name = serializers.CharField(
        source="production_manager.get_full_name", read_only=True
    )
    materiales = MaterialProduccionSerializer(many=True, read_only=True)

    class Meta:
        model = LoteProduccion
        fields = [
            "id",
            "product",
            "product_name",
            "product_code",
            "batch_code",
            "production_date",
            "produced_quantity",
            "unit",
            "unit_name",
            "unit_symbol",
            "status",
            "production_manager",
            "production_manager_name",
            "materiales",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
