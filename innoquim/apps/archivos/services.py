"""
Servicio para comunicarse con el microservicio file-manager.
Gestiona la subida y descarga de archivos a Google Drive.
"""

import requests
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FileManagerService:
    """
    Cliente para comunicarse con el servicio file-manager (FastAPI).
    
    El servicio file-manager corre en un contenedor Docker separado
    y se encarga de subir archivos a Google Drive.
    """
    
    def __init__(self):
        """
        Inicializa el servicio con la URL del file-manager.
        
        En desarrollo: http://localhost:8001
        En produccion (Docker): http://file-manager:8001
        """
        # URL del servicio file-manager
        # Usar 'file-manager' (nombre del contenedor) cuando se ejecuta en Docker
        # Usar 'localhost' cuando se ejecuta localmente
        self.base_url = getattr(
            settings, 
            'FILE_MANAGER_URL', 
            'http://file-manager:8001'
        )
        
        # Timeout para las peticiones (30 segundos)
        self.timeout = 30
    
    def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        tipo_reporte: str,
        descripcion: Optional[str] = None
    ) -> Dict:
        """
        Sube un archivo PDF al servicio file-manager.
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre del archivo (ej: reporte_inventario.pdf)
            tipo_reporte: Tipo de reporte (inventario, clientes, etc)
            descripcion: Descripcion opcional del archivo
        
        Returns:
            Dict con informacion del archivo subido:
            {
                'archivo_id': 'ID en Google Drive',
                'nombre': 'nombre.pdf',
                'google_drive_id': 'ID',
                'url_descarga': 'URL',
                'tamaño': 12345,
                'fecha_subida': '2025-11-20T...'
            }
        
        Raises:
            Exception: Si falla la comunicacion con file-manager
        """
        url = f"{self.base_url}/api/archivos/upload"
        
        # Preparar datos del formulario
        files = {
            'file': (filename, file_content, 'application/pdf')
        }
        
        data = {
            'tipo_reporte': tipo_reporte,
        }
        
        if descripcion:
            data['descripcion'] = descripcion
        
        try:
            logger.info(f"Subiendo archivo a file-manager: {filename}")
            
            # Hacer peticion POST al file-manager
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            # Verificar si fue exitoso
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Archivo subido exitosamente: {result.get('archivo_id')}")
            
            return result
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexion con file-manager: {e}")
            raise Exception(
                "No se pudo conectar con el servicio de archivos. "
                "Verifique que el contenedor file-manager este corriendo."
            )
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout al subir archivo: {e}")
            raise Exception(
                "El servicio de archivos tardo demasiado en responder. "
                "Intente nuevamente."
            )
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP al subir archivo: {e}")
            error_detail = response.json().get('detail', 'Error desconocido')
            raise Exception(f"Error al subir archivo: {error_detail}")
        
        except Exception as e:
            logger.error(f"Error inesperado al subir archivo: {e}")
            raise Exception(f"Error al subir archivo: {str(e)}")
    
    def delete_file(self, google_drive_id: str) -> bool:
        """
        Elimina un archivo de Google Drive via file-manager.
        
        Args:
            google_drive_id: ID del archivo en Google Drive
        
        Returns:
            True si se elimino correctamente, False en caso contrario
        """
        url = f"{self.base_url}/api/archivos/{google_drive_id}"
        
        try:
            logger.info(f"Eliminando archivo de Google Drive: {google_drive_id}")
            
            response = requests.delete(url, timeout=self.timeout)
            response.raise_for_status()
            
            logger.info(f"Archivo eliminado exitosamente: {google_drive_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return False
    
    def get_file_info(self, google_drive_id: str) -> Optional[Dict]:
        """
        Obtiene informacion de un archivo en Google Drive.
        
        Args:
            google_drive_id: ID del archivo en Google Drive
        
        Returns:
            Dict con informacion del archivo o None si hay error
        """
        url = f"{self.base_url}/api/archivos/{google_drive_id}/info"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error al obtener info del archivo: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Verifica si el servicio file-manager esta disponible.
        
        Returns:
            True si el servicio responde, False en caso contrario
        """
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        
        except Exception:
            return False


# Instancia singleton del servicio
file_manager_service = FileManagerService()