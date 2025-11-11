from rest_framework import serializers
from .models import PedidoMaterial


class PedidoMaterialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo PedidoMaterial.
    """
    
    # Campos adicionales de solo lectura
    nombre_proveedor = serializers.CharField(
        source='proveedor_id.nombre_empresa',
        read_only=True
    )
    
    nombre_usuario = serializers.CharField(
        source='usuario_registro.get_full_name',
        read_only=True
    )
    
    username = serializers.CharField(
        source='usuario_registro.username',
        read_only=True
    )
    
    class Meta:
        model = PedidoMaterial
        fields = [
            'pedido_material_id',
            'proveedor_id',
            'nombre_proveedor',
            'usuario_registro',
            'nombre_usuario',
            'username',
            'fecha_pedido',
            'fecha_entrega_esperada',
            'numero_orden_compra',
            'observaciones',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'pedido_material_id',
            'fecha_creacion',
            'fecha_actualizacion'
        ]