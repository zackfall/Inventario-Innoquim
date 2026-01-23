from rest_framework import serializers
from .models import MateriaPrima


class MateriaPrimaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MateriaPrima.
    Convierte objetos Python <-> JSON para la API REST.
    """
    
    # Campos adicionales de solo lectura
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
            'stock',
            'stock_minimo',
            'stock_maximo',
            'costo_promedio',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        stock_minimo = data.get('stock_minimo', 0)
        stock_maximo = data.get('stock_maximo')
        
        if stock_maximo is not None and stock_maximo <= stock_minimo:
            raise serializers.ValidationError({
                'stock_maximo': 'El stock máximo debe ser mayor que el stock mínimo.'
            })
        
        return data