from rest_framework import serializers
from .models import MateriaPrima


class MateriaPrimaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MateriaPrima.
    Convierte objetos Python <-> JSON para la API REST.
    """
    
    # Campo adicional de solo lectura para mostrar el nombre de la unidad
    # Evita hacer una peticion extra para obtener el nombre
    nombre_unidad = serializers.CharField(source='unidad_id.nombre', read_only=True)
    
    class Meta:
        model = MateriaPrima
        fields = [
            'materia_prima_id',
            'nombre',
            'codigo',
            'descripcion',
            'unidad_id',
            'nombre_unidad',  # Campo extra para lectura
            'densidad',
            'stock',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        # Campos que NO se pueden modificar via API
        read_only_fields = ['materia_prima_id', 'fecha_creacion', 'fecha_actualizacion']