from rest_framework import serializers
from .models import MaterialProduccion


class MaterialProduccionSerializer(serializers.ModelSerializer):
    batch_code = serializers.CharField(source="batch.batch_code", read_only=True)
    raw_material_name = serializers.CharField(
        source="raw_material.name", read_only=True
    )
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = MaterialProduccion
        fields = [
            "id",
            "batch",
            "batch_code",
            "raw_material",
            "raw_material_name",
            "used_quantity",
            "unit",
            "unit_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
