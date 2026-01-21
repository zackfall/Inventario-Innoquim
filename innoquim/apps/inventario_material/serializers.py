from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import InventarioMaterial


class InventarioMaterialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo InventarioMaterial (genérico).
    Convierte objetos Python <-> JSON para la API REST.
    """

    # Campos legibles dinámicos
    item_tipo = serializers.SerializerMethodField(read_only=True)
    item_id_externo = serializers.CharField(source='object_id')
    item_nombre = serializers.SerializerMethodField(read_only=True)

    nombre_almacen = serializers.CharField(
        source='almacen_id.nombre',
        read_only=True
    )

    nombre_unidad = serializers.CharField(
        source='unidad_id.nombre',
        read_only=True
    )

    simbolo_unidad = serializers.CharField(
        source='unidad_id.simbolo',
        read_only=True
    )

    class Meta:
        model = InventarioMaterial
        fields = [
            'inventario_material_id',
            'content_type',
            'item_tipo',
            'object_id',
            'item_id_externo',
            'item_nombre',
            'almacen_id',
            'nombre_almacen',
            'unidad_id',
            'nombre_unidad',
            'simbolo_unidad',
            'cantidad',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['inventario_material_id', 'fecha_creacion', 'fecha_actualizacion']

    def get_item_tipo(self, obj):
        if not obj.content_type:
            return None
        model = obj.content_type.model
        if model == 'materia_prima':
            return 'MATERIA_PRIMA'
        if model == 'producto':
            return 'PRODUCTO'
        return model.upper()

    def get_item_nombre(self, obj):
        item = getattr(obj, 'item', None)
        if not item:
            return None
        return getattr(item, 'nombre', None) or getattr(item, 'name', None) or str(obj.object_id)