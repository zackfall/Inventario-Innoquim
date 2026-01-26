# archivos/serializers.py
"""
Serializers para el modelo Archivo y operaciones con Google Drive.
"""

from rest_framework import serializers
from .models import Archivo
from django.contrib.auth import get_user_model

User = get_user_model()


class ArchivoSerializer(serializers.ModelSerializer):
    """
    Serializer principal para el modelo Archivo.
    Incluye información del usuario que generó el archivo.
    """
    
    usuario_generador_nombre = serializers.SerializerMethodField()
    tamaño_legible = serializers.SerializerMethodField()
    
    class Meta:
        model = Archivo
        fields = [
            'archivo_id',
            'nombre',
            'tipo_reporte',
            'google_drive_id',
            'url_descarga',
            'tamaño',
            'tamaño_legible',
            'descripcion',
            'usuario_generador',
            'usuario_generador_nombre',
            'fecha_generacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'archivo_id',
            'google_drive_id',
            'url_descarga',
            'fecha_generacion',
            'fecha_actualizacion',
        ]
    
    def get_usuario_generador_nombre(self, obj):
        """Retorna el nombre del usuario."""
        if obj.usuario_generador:
            # Intenta obtener el campo 'name', si no existe usa 'username'
            return getattr(obj.usuario_generador, 'name', obj.usuario_generador.username)
        return None
    
    def get_tamaño_legible(self, obj):
        """Retorna el tamaño en formato legible."""
        return obj.get_tamaño_legible()


class ArchivoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar archivos.
    Solo incluye campos esenciales para mejorar performance.
    """
    
    usuario_generador_nombre = serializers.SerializerMethodField()
    tamaño_legible = serializers.SerializerMethodField()
    
    class Meta:
        model = Archivo
        fields = [
            'archivo_id',
            'nombre',
            'tipo_reporte',
            'tamaño_legible',
            'usuario_generador_nombre',
            'fecha_generacion',
        ]
    
    def get_usuario_generador_nombre(self, obj):
        if obj.usuario_generador:
            return obj.usuario_generador.username
        return None
    
    def get_tamaño_legible(self, obj):
        return obj.get_tamaño_legible()


class ArchivoUploadSerializer(serializers.Serializer):
    """
    Serializer para subir archivos a Google Drive.
    Valida el archivo y los metadatos antes de subirlo.
    """
    
    archivo = serializers.FileField(
        required=True,
        help_text='Archivo a subir (PDF, Excel, Word, etc.)'
    )
    
    tipo_reporte = serializers.CharField(
        required=True,
        max_length=30,
        help_text='Tipo de reporte'
    )
    
    descripcion = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text='Descripción opcional del archivo'
    )
    
    def validate_archivo(self, value):
        """
        Valida el archivo subido.
        Puedes agregar validaciones de tamaño, tipo MIME, etc.
        """
        # Validar tamaño máximo (50 MB)
        max_size = 50 * 1024 * 1024  # 50 MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f'El archivo es muy grande. Tamaño máximo: 50 MB'
            )
        
        # Validar extensiones permitidas
        allowed_extensions = ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.csv']
        file_extension = value.name.lower().split('.')[-1]
        
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(allowed_extensions)}'
            )
        
        return value


class ArchivoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado con toda la información del archivo.
    Incluye información completa del usuario.
    """
    
    usuario_generador_info = serializers.SerializerMethodField()
    tamaño_legible = serializers.SerializerMethodField()
    
    class Meta:
        model = Archivo
        fields = '__all__'
    
    def get_usuario_generador_info(self, obj):
        """Retorna información completa del usuario."""
        if obj.usuario_generador:
            return {
                'id': obj.usuario_generador.id,
                'username': obj.usuario_generador.username,
                'nombre': getattr(obj.usuario_generador, 'name', obj.usuario_generador.username),
                'email': obj.usuario_generador.email,
                'rol': getattr(obj.usuario_generador, 'rol', None),
            }
        return None
    
    def get_tamaño_legible(self, obj):
        return obj.get_tamaño_legible()