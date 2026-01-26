from rest_framework import serializers
from .models import LoteProduccion
from innoquim.apps.material_produccion.serializers import MaterialProduccionSerializer


class LoteProduccionSerializer(serializers.ModelSerializer):
    """Serializer para listar lotes (read-only extendido)"""
    
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_code = serializers.CharField(source="product.product_code", read_only=True)
    unit_name = serializers.CharField(source="unit.nombre", read_only=True)
    unit_symbol = serializers.CharField(source="unit.simbolo", read_only=True)
    almacen_name = serializers.CharField(source="almacen.nombre", read_only=True)
    production_manager_name = serializers.CharField(
        source="production_manager.get_full_name", read_only=True
    )
    materiales = MaterialProduccionSerializer(many=True, read_only=True)
    
    # NUEVO: Mostrar cantidad de materiales
    total_materiales = serializers.SerializerMethodField()

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
            "almacen",
            "almacen_name",
            "status",
            "production_manager",
            "production_manager_name",
            "costo_materiales",
            "costo_unitario_producto",
            "observaciones",
            "materiales",
            "total_materiales",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "completed_at",
            "costo_materiales",
            "costo_unitario_producto"
        ]
    
    def get_total_materiales(self, obj):
        return obj.materiales.count()


class LoteProduccionCreateSerializer(serializers.ModelSerializer):
    materiales = MaterialProduccionSerializer(many=True, required=False)

    class Meta:
        model = LoteProduccion
        fields = [
            "product",
            "batch_code",
            "production_date",
            "produced_quantity",
            "unit",
            "almacen",
            "status",
            "production_manager",
            "observaciones",
            "materiales",
        ]
    
    def create(self, validated_data):
        from innoquim.apps.material_produccion.models import MaterialProduccion
        
        materiales_data = validated_data.pop('materiales', [])
        
        # Crear el lote
        lote = LoteProduccion.objects.create(**validated_data)
        
        # Crear los materiales asociados
        for material_data in materiales_data:
            MaterialProduccion.objects.create(
                batch=lote,
                **material_data
            )
        
        # Calcular costos iniciales
        lote.calcular_costo_materiales()
        
        return lote