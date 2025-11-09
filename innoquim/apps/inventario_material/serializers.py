from rest_framework import serializers
from .models import InventarioMaterial


class InventarioMaterialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo InventarioMaterial.
    Convierte objetos Python <-> JSON para la API REST.
    """
    
    # Campos adicionales de solo lectura para mostrar nombres legibles
    # Evita hacer peticiones extra para obtener los nombres
    nombre_materia_prima = serializers.CharField(
        source='materia_prima_id.nombre',
        read_only=True
    )
    
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
            'materia_prima_id',
            'nombre_materia_prima',  # Campo extra
            'almacen_id',
            'nombre_almacen',  # Campo extra
            'unidad_id',
            'nombre_unidad',  # Campo extra
            'simbolo_unidad',  # Campo extra
            'cantidad',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        # Campos que NO se pueden modificar via API
        read_only_fields = ['inventario_material_id', 'fecha_creacion', 'fecha_actualizacion']