# archivos/views.py
"""
Views para gestionar archivos con Google Drive.
Implementa permisos: todos pueden ver, solo el creador puede eliminar.
"""

import os
import tempfile
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Archivo
from .serializers import (
    ArchivoSerializer,
    ArchivoListSerializer,
    ArchivoUploadSerializer,
    ArchivoDetailSerializer
)
from .services import get_drive_service


class ArchivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar archivos en Google Drive.
    
    Permisos:
    - Todos los usuarios autenticados pueden: listar, ver, subir
    - Solo el creador puede: eliminar su propio archivo
    
    Endpoints:
    - GET /api/archivos/ - Lista todos los archivos
    - POST /api/archivos/ - Sube un nuevo archivo
    - GET /api/archivos/{id}/ - Obtiene detalles de un archivo
    - DELETE /api/archivos/{id}/ - Elimina un archivo (solo creador)
    - GET /api/archivos/{id}/download/ - Obtiene URL de descarga
    """
    
    queryset = Archivo.objects.select_related('usuario_generador').all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'archivo_id'
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return ArchivoListSerializer
        elif self.action == 'retrieve':
            return ArchivoDetailSerializer
        elif self.action == 'create':
            return ArchivoUploadSerializer
        return ArchivoSerializer
    
    def get_queryset(self):
        """
        Filtra archivos según query params.
        Permite filtrar por tipo_reporte y usuario.
        """
        queryset = super().get_queryset()
        
        # Filtrar por tipo de reporte
        tipo_reporte = self.request.query_params.get('tipo_reporte', None)
        if tipo_reporte:
            queryset = queryset.filter(tipo_reporte=tipo_reporte)
        
        # Filtrar por usuario (mis archivos)
        mis_archivos = self.request.query_params.get('mis_archivos', None)
        if mis_archivos and mis_archivos.lower() == 'true':
            queryset = queryset.filter(usuario_generador=self.request.user)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Sube un archivo a Google Drive y guarda metadatos en BD.
        
        Flujo:
        1. Valida el archivo
        2. Guarda temporalmente el archivo
        3. Sube a Google Drive
        4. Guarda metadatos en BD
        5. Elimina archivo temporal
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        archivo_subido = serializer.validated_data['archivo']
        tipo_reporte = serializer.validated_data['tipo_reporte']
        descripcion = serializer.validated_data.get('descripcion', '')
        
        # Crear archivo temporal
        temp_file = None
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as temp_file:
                for chunk in archivo_subido.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Determinar MIME type
            mime_types = {
                '.pdf': 'application/pdf',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.csv': 'text/csv',
            }
            file_extension = os.path.splitext(archivo_subido.name)[1].lower()
            mime_type = mime_types.get(file_extension, 'application/octet-stream')
            
            # Subir a Google Drive
            drive_service = get_drive_service()
            drive_result = drive_service.upload_file(
                file_path=temp_file_path,
                file_name=archivo_subido.name,
                mime_type=mime_type
            )
            
            # Guardar en BD
            archivo = Archivo.objects.create(
                nombre=archivo_subido.name,
                tipo_reporte=tipo_reporte,
                descripcion=descripcion,
                google_drive_id=drive_result['id'],
                url_descarga=drive_result['webContentLink'],
                tamaño=archivo_subido.size,
                usuario_generador=request.user
            )
            
            # Eliminar archivo temporal
            os.remove(temp_file_path)
            
            # Retornar respuesta
            response_serializer = ArchivoDetailSerializer(archivo)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            # Limpiar archivo temporal en caso de error
            if temp_file and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return Response(
                {'error': f'Error al subir archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un archivo (solo si el usuario es el creador).
        Elimina de Google Drive y de la BD.
        """
        archivo = self.get_object()
        
        # Verificar que el usuario sea el creador
        if archivo.usuario_generador != request.user:
            return Response(
                {'error': 'No tienes permisos para eliminar este archivo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Eliminar de Google Drive
            drive_service = get_drive_service()
            drive_service.delete_file(archivo.google_drive_id)
            
            # Eliminar de BD
            archivo.delete()
            
            return Response(
                {'message': 'Archivo eliminado exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error al eliminar archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, archivo_id=None):
        """
        Retorna la URL de descarga directa del archivo.
        
        GET /api/archivos/{id}/download/
        """
        archivo = self.get_object()
        
        return Response({
            'archivo_id': archivo.archivo_id,
            'nombre': archivo.nombre,
            'url_descarga': archivo.url_descarga,
            'tamaño': archivo.tamaño,
            'tamaño_legible': archivo.get_tamaño_legible()
        })
    
    @action(detail=False, methods=['get'])
    def tipos_reporte(self, request):
        """
        Retorna los tipos de reporte disponibles.
        
        GET /api/archivos/tipos_reporte/
        """
        tipos = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Archivo.TIPO_REPORTE_CHOICES
        ]
        return Response({'tipos_reporte': tipos})
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Retorna estadísticas de archivos.
        
        GET /api/archivos/estadisticas/
        """
        queryset = self.get_queryset()
        
        # Estadísticas por tipo de reporte
        estadisticas_tipo = {}
        for tipo, label in Archivo.TIPO_REPORTE_CHOICES:
            count = queryset.filter(tipo_reporte=tipo).count()
            estadisticas_tipo[label] = count
        
        # Estadísticas del usuario actual
        mis_archivos = queryset.filter(usuario_generador=request.user).count()
        
        return Response({
            'total_archivos': queryset.count(),
            'mis_archivos': mis_archivos,
            'por_tipo': estadisticas_tipo,
            'espacio_usado': sum(a.tamaño for a in queryset)
        })