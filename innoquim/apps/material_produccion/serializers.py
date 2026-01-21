from rest_framework import serializers
from .models import MaterialProduccion


class MaterialProduccionSerializer(serializers.ModelSerializer):
    batch_code = serializers.CharField(source="batch.batch_code", read_only=True)
    raw_material_name = serializers.CharField(
        source="raw_material.name", read_only=True
    )
    raw_material_codigo = serializers.CharField(
        source="raw_material.materia_prima_codigo", read_only=True
    )
    raw_material_stock = serializers.DecimalField(
        source="raw_material.stock_actual",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    raw_material_stock_minimo = serializers.DecimalField(
        source="raw_material.stock_minimo",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    raw_material_stock_maximo = serializers.DecimalField(
        source="raw_material.stock_maximo",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    unit_name = serializers.CharField(source="unit.nombre", read_only=True)
    unit_symbol = serializers.CharField(source="unit.simbolo", read_only=True)

    class Meta:
        model = MaterialProduccion
        fields = [
            "id",
            "batch",
            "batch_code",
            "raw_material",
            "raw_material_name",
            "raw_material_codigo",
            "raw_material_stock",
            "raw_material_stock_minimo",
            "raw_material_stock_maximo",
            "used_quantity",
            "unit",
            "unit_name",
            "unit_symbol",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
