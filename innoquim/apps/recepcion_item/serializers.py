from rest_framework import serializers
from .models import RecepcionItem
from innoquim.apps.recepcion_material.serializers import RecepcionMaterialSerializer
from innoquim.apps.materia_prima.serializers import MateriaPrimaSerializer

# =================================================================
# SERIALIZADOR RECEPCION ITEM
# =================================================================
class RecepcionItemSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo RecepcionItem.
    Convierte objetos Python <-> JSON para la API REST.
    
    Incluye detalles completos de las relaciones (recepción, materia prima, unidad)
    para facilitar la visualización de datos sin necesidad de peticiones adicionales.
    """
    
    # Campos anidados de solo lectura que muestran los detalles completos
    # Estos permiten visualizar toda la información relacionada sin peticiones adicionales
    recepcion_material_detail = RecepcionMaterialSerializer(
        source='id_recepcion_material',
        read_only=True,
        help_text='Detalles completos de la recepción padre'
    )
    
    # Detalle de la materia prima recibida
    materia_prima_detail = MateriaPrimaSerializer(
        source='id_materia_prima',
        read_only=True,
        help_text='Detalles completos de la materia prima'
    )
    

    class Meta:
        model = RecepcionItem
        fields = [
            'id',
            # Recepción padre
            'id_recepcion_material',
            'recepcion_material_detail',
            # Materia prima recibida
            'id_materia_prima',
            'materia_prima_detail',
            # Cantidad y unidad
            'cantidad',
            'id_unidad',
            # Información de lote
            'lote',
            # Notas adicionales
            'observaciones',
        ]