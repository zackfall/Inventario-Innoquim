"""
Serializers para el modelo Archivo.
"""

from rest_framework import serializers
from .models import Archivo


class ArchivoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Archivo.
    Convierte objetos Archivo <-> JSON para la API REST.
    """
    
    # Campos adicionales de solo lectura
    tipo_reporte_display = serializers.CharField(
        source='get_tipo_reporte_display',
        read_only=True
    )
    
    nombre_usuario = serializers.CharField(
        source='usuario_generador.get_full_name',
        read_only=True
    )
    
    username = serializers.CharField(
        source='usuario_generador.username',
        read_only=True
    )
    
    tamaño_legible = serializers.SerializerMethodField()
    
    class Meta:
        model = Archivo
        fields = [
            'archivo_id',
            'nombre',
            'tipo_reporte',
            'tipo_reporte_display',
            'google_drive_id',
            'url_descarga',
            'tamaño',
            'tamaño_legible',
            'descripcion',
            'usuario_generador',
            'nombre_usuario',
            'username',
            'fecha_generacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'archivo_id',
            'google_drive_id',
            'url_descarga',
            'tamaño',
            'fecha_generacion',
            'fecha_actualizacion',
        ]
    
    def get_tamaño_legible(self, obj):
        """Retorna el tamaño en formato legible (KB, MB, etc)"""
        tamaño = obj.tamaño
        for unit in ['B', 'KB', 'MB', 'GB']:
            if tamaño < 1024.0:
                return f"{tamaño:.1f} {unit}"
            tamaño /= 1024.0
        return f"{tamaño:.1f} TB"


class ArchivoUploadSerializer(serializers.Serializer):
    """
    Serializer para subir archivos PDF.
    """
    
    # archivo: el PDF en base64 o como file upload
    archivo = serializers.FileField(
        required=True,
        help_text='Archivo PDF a subir'
    )
    
    nombre = serializers.CharField(
        max_length=255,
        required=False,
        help_text='Nombre descriptivo del archivo (opcional, se usa el nombre del archivo si no se proporciona)'
    )
    
    tipo_reporte = serializers.ChoiceField(
        choices=Archivo.TIPO_REPORTE_CHOICES,
        required=True,
        help_text='Tipo de reporte'
    )
    
    descripcion = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Descripcion opcional del reporte'
    )
    
    def validate_archivo(self, value):
        """Valida que el archivo sea un PDF"""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Solo se permiten archivos PDF")
        
        # Validar tamaño (maximo 10MB)
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("El archivo no puede superar 10MB")
        
        return value