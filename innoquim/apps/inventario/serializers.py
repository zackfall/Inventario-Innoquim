from rest_framework import serializers
from .models import Kardex
from django.contrib.contenttypes.models import ContentType


class KardexSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de registros de Kardex.
    Los registros de Kardex NO se crean/editan directamente por API,
    sino mediante el método Kardex.registrar_movimiento()
    """
    
    # Campos calculados para mostrar información del item
    item_tipo = serializers.SerializerMethodField()
    item_codigo = serializers.SerializerMethodField()
    item_nombre = serializers.SerializerMethodField()
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.name', read_only=True)
    
    class Meta:
        model = Kardex
        fields = [
            'id',
            'fecha',
            'almacen',
            'almacen_nombre',
            'item_tipo',
            'item_codigo',
            'item_nombre',
            'tipo_movimiento',
            'motivo',
            'cantidad',
            'costo_unitario',
            'costo_total',
            'saldo_cantidad',
            'saldo_costo_total',
            'saldo_costo_promedio',
            'referencia_id',
            'observaciones',
            'usuario',
            'usuario_nombre',
        ]
        # Todos los campos son de solo lectura (lista explícita)
        read_only_fields = [
            'id',
            'fecha',
            'almacen',
            'almacen_nombre',
            'item_tipo',
            'item_codigo',
            'item_nombre',
            'tipo_movimiento',
            'motivo',
            'cantidad',
            'costo_unitario',
            'costo_total',
            'saldo_cantidad',
            'saldo_costo_total',
            'saldo_costo_promedio',
            'referencia_id',
            'observaciones',
            'usuario',
            'usuario_nombre',
        ]
    
    def get_item_tipo(self, obj):
        """Retorna el tipo de item (MateriaPrima o Producto)"""
        return obj.content_type.model
    
    def get_item_codigo(self, obj):
        """Retorna el código del item"""
        if obj.item:
            if hasattr(obj.item, 'materia_prima_id'):
                return obj.item.materia_prima_id
            elif hasattr(obj.item, 'product_code'):
                return obj.item.product_code
        return None
    
    def get_item_nombre(self, obj):
        """Retorna el nombre del item"""
        if obj.item:
            if hasattr(obj.item, 'nombre'):
                return obj.item.nombre
            elif hasattr(obj.item, 'name'):
                return obj.item.name
        return None


class KardexSaldoSerializer(serializers.Serializer):
    """
    Serializer para consultar saldos actuales.
    No es un ModelSerializer porque representa datos calculados.
    """
    materia_prima_id = serializers.CharField(required=False)
    producto_id = serializers.IntegerField(required=False)
    almacen_id = serializers.IntegerField(required=True)
    cantidad = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    costo_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    costo_promedio = serializers.DecimalField(max_digits=12, decimal_places=4, read_only=True)
