from rest_framework import serializers
from .models import MaterialProduccion


class MaterialProduccionSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(
        source="raw_material.nombre", read_only=True
    )
    raw_material_code = serializers.CharField(
        source="raw_material.codigo", read_only=True
    )
    unit_name = serializers.CharField(source="unit.nombre", read_only=True)
    unit_symbol = serializers.CharField(source="unit.simbolo", read_only=True)
    
    stock_disponible = serializers.SerializerMethodField()

    class Meta:
        model = MaterialProduccion
        fields = [
            "id",
            "batch",
            "raw_material",
            "raw_material_name",
            "raw_material_code",
            "used_quantity",
            "unit",
            "unit_name",
            "unit_symbol",
            "costo_unitario",
            "costo_total",
            "stock_disponible",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "costo_unitario",
            "costo_total"
        ]
    
    def get_stock_disponible(self, obj):
        """Retorna el stock actual de la materia prima"""
        return float(obj.raw_material.stock)