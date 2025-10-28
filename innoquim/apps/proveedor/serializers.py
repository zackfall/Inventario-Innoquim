from rest_framework import serializers
from .models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    """
    Serializer para convertir objetos Proveedor a JSON y viceversa.
    Utilizado en las operaciones de la API REST.
    """
    
    class Meta:
        model = Proveedor
        fields = [
            'proveedor_id',
            'ruc',
            'nombre_empresa',
            'nombre_contacto',
            'telefono',
            'email',
            'direccion',
            'tipo_producto',
            'fecha_registro',
            'fecha_actualizacion'
        ]
        
        # Campos de solo lectura (no modificables por API)
        read_only_fields = ['proveedor_id', 'fecha_registro', 'fecha_actualizacion']
    
    def validate_ruc(self, value):
        """
        Validación adicional para el RUC.
        Asegura que solo contenga dígitos.
        """
        if not value.isdigit():
            raise serializers.ValidationError("El RUC debe contener solo números")
        return value