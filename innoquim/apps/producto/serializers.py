from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    nombre_categoria = serializers.CharField(source="categoria_id.nombre", read_only=True)
    tipo_categoria = serializers.CharField(source="categoria_id.get_tipo_display", read_only=True)

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
            "stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_product_code(self, value):
        if self.instance and self.instance.product_code == value:
            return value
        if Producto.objects.filter(product_code=value).exists():
            raise serializers.ValidationError("El código de producto ya existe.")
        return value