from rest_framework import serializers
from .models import MateriaPrima


class MateriaPrimaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MateriaPrima.
    Convierte objetos Python <-> JSON para la API REST.
    """
    
    nombre_unidad = serializers.CharField(source='unidad_id.nombre', read_only=True)
    
    nombre_categoria = serializers.CharField(source='categoria_id.nombre', read_only=True)
    tipo_categoria = serializers.CharField(source='categoria_id.get_tipo_display', read_only=True)
    
    class Meta:
        model = MateriaPrima
        fields = [
            'materia_prima_id',
            'nombre',
            'codigo',
            'descripcion',
            'categoria_id',           
            'nombre_categoria',       
            'tipo_categoria',         
            'unidad_id',
            'nombre_unidad',
            'densidad',
            'costo_promedio',
            'stock',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']