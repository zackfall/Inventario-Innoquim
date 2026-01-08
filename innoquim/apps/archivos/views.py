"""
Views para gestionar archivos PDF.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import logging

from .models import Archivo
from .serializers import ArchivoSerializer, ArchivoUploadSerializer
from .services import file_manager_service

logger = logging.getLogger(__name__)


class ArchivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Archivo.
    
    Endpoints:
    - GET    /api/archivos/              -> Listar archivos
    - POST   /api/archivos/guardar/      -> Subir archivo
    - GET    /api/archivos/{id}/         -> Ver detalle
    - DELETE /api/archivos/{id}/         -> Eliminar archivo
    - GET    /api/archivos/health/       -> Verificar estado del servicio
    """
    
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = [IsAuthenticated]  # Requiere autenticacion
    
    def get_queryset(self):
        """
        Permite filtrar archivos via query params.
        Ejemplos:
        - /api/archivos/?tipo_reporte=inventario
        - /api/archivos/?usuario_generador=1
        """
        queryset = Archivo.objects.all()
        
        # Filtrar por tipo de reporte
        tipo_reporte = self.request.query_params.get('tipo_reporte', None)
        if tipo_reporte:
            queryset = queryset.filter(tipo_reporte=tipo_reporte)
        
        # Filtrar por usuario (opcional)
        usuario_id = self.request.query_params.get('usuario_generador', None)
        if usuario_id:
            queryset = queryset.filter(usuario_generador_id=usuario_id)
        
        # Filtrar por fecha (opcional)
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        if fecha_desde:
            queryset = queryset.filter(fecha_generacion__gte=fecha_desde)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='guardar')
    def guardar_archivo(self, request):
        """
        Endpoint para subir un archivo PDF.
        
        POST /api/archivos/guardar/
        
        Body (multipart/form-data):
        - archivo: archivo PDF
        - tipo_reporte: tipo de reporte
        - nombre: nombre opcional
        - descripcion: descripcion opcional
        
        Returns:
            Informacion del archivo guardado
        """
        serializer = ArchivoUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener datos validados
            archivo = serializer.validated_data['archivo']
            tipo_reporte = serializer.validated_data['tipo_reporte']
            nombre = serializer.validated_data.get('nombre', archivo.name)
            descripcion = serializer.validated_data.get('descripcion', '')
            
            # Leer contenido del archivo
            archivo.seek(0)  # Asegurar que estamos al inicio del archivo
            file_content = archivo.read()
            
            # Subir a Google Drive via file-manager
            logger.info(f"Subiendo archivo: {nombre}")
            result = file_manager_service.upload_file(
                file_content=file_content,
                filename=nombre,
                tipo_reporte=tipo_reporte,
                descripcion=descripcion
            )
            
            # Guardar metadatos en la base de datos
            archivo_obj = Archivo.objects.create(
                nombre=nombre,
                tipo_reporte=tipo_reporte,
                google_drive_id=result['google_drive_id'],
                url_descarga=result['url_descarga'],
                tamaño=result['tamaño'],
                descripcion=descripcion,
                usuario_generador=request.user  # Usuario autenticado
            )
            
            # Serializar y retornar
            response_serializer = ArchivoSerializer(archivo_obj)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un archivo (de la BD y de Google Drive).
        
        DELETE /api/archivos/{id}/
        """
        archivo = self.get_object()
        
        try:
            # Eliminar de Google Drive
            logger.info(f"Eliminando archivo: {archivo.archivo_id}")
            file_manager_service.delete_file(archivo.google_drive_id)
            
            # Eliminar de la base de datos
            archivo.delete()
            
            return Response(
                {'message': 'Archivo eliminado exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='health')
    def health_check(self, request):
        """
        Verifica el estado del servicio file-manager.
        
        GET /api/archivos/health/
        """
        is_healthy = file_manager_service.health_check()
        
        return Response({
            'file_manager_status': 'healthy' if is_healthy else 'unhealthy',
            'database_status': 'healthy',
            'archivos_count': Archivo.objects.count()
        })