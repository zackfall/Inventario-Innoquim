from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    nombre_categoria = serializers.CharField(source="categoria_id.nombre", read_only=True)
    tipo_categoria = serializers.CharField(source="categoria_id.get_tipo_display", read_only=True)
    
    # Campos calculados para estado del stock
    stock_status = serializers.CharField(read_only=True)
    necesita_reabastecimiento = serializers.BooleanField(read_only=True)
    sobre_inventario = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "product_code",
            "name",
            "description",
            "categoria_id",        
            "nombre_categoria",    
            "tipo_categoria",    
            "unit",
            "unit_name",
            "weight",
            "price",
            "costo_unitario",
            "stock",
            "stock_minimo",
            "stock_maximo",
            "stock_status",
            "necesita_reabastecimiento",
            "sobre_inventario",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        stock_minimo = data.get('stock_minimo', 0)
        stock_maximo = data.get('stock_maximo')
        
        if stock_maximo is not None and stock_maximo <= stock_minimo:
            raise serializers.ValidationError({
                'stock_maximo': 'El stock máximo debe ser mayor que el stock mínimo.'
            })
        
        return data