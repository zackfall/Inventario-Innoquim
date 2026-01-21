# backend/apps/archivos/services.py
"""
Cliente HTTP para comunicarse con el File Manager Service.
Django Backend NO interactúa directamente con Google Drive.
"""

import requests
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FileManagerClient:
    """
    Cliente para comunicarse con el File Manager Service (FastAPI).
    
    El File Manager es un servicio independiente que maneja Google Drive.
    Django solo guarda metadatos y delega la gestión de archivos al File Manager.
    """
    
    def __init__(self):
        """
        Inicializa el cliente con la URL del File Manager.
        """
        self.base_url = getattr(
            settings, 
            'FILE_MANAGER_URL', 
            'http://localhost:8001' 
        )
        self.timeout = 30
    
    def upload_file(self, file_path: str, file_name: str) -> Dict:
        """
        Sube un archivo al File Manager para que lo guarde en Google Drive.
        
        Args:
            file_path: Ruta local del archivo temporal
            file_name: Nombre del archivo
        
        Returns:
            dict con google_drive_id, url_descarga, tamaño
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/pdf')}
                data = {
                    'tipo_reporte': 'archivo',
                    'descripcion': ''
                }
                
                response = requests.post(
                    f"{self.base_url}/api/archivos/upload",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Mapear la respuesta del File Manager al formato esperado
                return {
                    'google_drive_id': result.get('google_drive_id') or result.get('archivo_id'),
                    'url_descarga': result.get('url_descarga'),
                    'tamaño': result.get('tamaño')
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al subir archivo al File Manager: {e}")
            raise Exception(f"Error al comunicarse con File Manager: {str(e)}")
    
        def delete_file(self, google_drive_id: str) -> bool:
            """
            Solicita al File Manager que elimine un archivo de Google Drive.

            Args:
                google_drive_id: ID del archivo en Google Drive
        
            Returns:
                True si se eliminó exitosamente
            """
            try:
                response = requests.delete(
                    f"{self.base_url}/api/archivos/{google_drive_id}",
                    timeout=self.timeout
                )
            
                response.raise_for_status()
                return True
        
            except requests.exceptions.RequestException as e:
                logger.error(f"Error al eliminar archivo del File Manager: {e}")
                raise Exception(f"Error al comunicarse con File Manager: {str(e)}")
    
    def get_file_info(self, google_drive_id: str) -> Optional[Dict]:
        """
        Obtiene información de un archivo desde el File Manager.
        
        Args:
            google_drive_id: ID del archivo en Google Drive
        
        Returns:
            Diccionario con información del archivo o None si no existe
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/archivos/{google_drive_id}/info",
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error al obtener info del archivo: {e}")
            raise Exception(f"Error al comunicarse con File Manager: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al comunicarse con File Manager: {e}")
            raise Exception(f"Error al comunicarse con File Manager: {str(e)}")
    
    def health_check(self) -> Dict:
        """
        Verifica que el File Manager esté disponible.
        
        Returns:
            Estado del File Manager
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"File Manager no disponible: {e}")
            return {
                "status": "unavailable",
                "error": str(e)
            }


# Instancia singleton del cliente
_file_manager_client = None

def get_file_manager_client() -> FileManagerClient:
    """
    Retorna una instancia singleton del cliente del File Manager.
    """
    global _file_manager_client
    if _file_manager_client is None:
        _file_manager_client = FileManagerClient()
    return _file_manager_client