# archivos/services.py
"""
Servicio para interactuar con Google Drive API usando OAuth 2.0.
Adaptado para Django REST Framework.
"""

import os
import io
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError


class GoogleDriveService:
    """
    Servicio para gestionar archivos en Google Drive.
    Compatible con cuentas personales de Google usando OAuth 2.0.
    """
    
    # Scope necesario para crear y gestionar archivos
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        """
        Inicializa el servicio usando configuración de Django settings.
        """
        self.credentials_path = settings.GOOGLE_DRIVE_CREDENTIALS_PATH
        self.token_path = settings.GOOGLE_DRIVE_TOKEN_PATH
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        self.credentials = None
        self.service = None
        
        self._authenticate()
    
    def _authenticate(self):
        """
        Autentica con Google Drive usando OAuth 2.0.
        Si ya existe un token válido, lo usa. Si no, inicia el flujo OAuth.
        """
        creds = None
        
        # Cargar token existente
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path, 
                self.SCOPES
            )
        
        # Si no hay credenciales válidas, solicitar login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refrescar token expirado
                creds.refresh(Request())
            else:
                # Iniciar flujo OAuth
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, 
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales para la próxima vez
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def upload_file(self, file_path: str, file_name: str, mime_type: str = 'application/pdf') -> dict:
        """
        Sube un archivo a Google Drive.
        
        Args:
            file_path: Ruta local del archivo a subir
            file_name: Nombre que tendrá el archivo en Drive
            mime_type: Tipo MIME del archivo
        
        Returns:
            dict con 'id', 'webViewLink' y 'webContentLink'
        
        Raises:
            HttpError: Si hay un error al subir el archivo
        """
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Hacer el archivo público para lectura
            self.service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            return {
                'id': file.get('id'),
                'webViewLink': file.get('webViewLink'),
                'webContentLink': file.get('webContentLink')
            }
        
        except HttpError as error:
            raise Exception(f'Error al subir archivo a Google Drive: {error}')
    
    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Descarga un archivo de Google Drive.
        
        Args:
            file_id: ID del archivo en Google Drive
            destination_path: Ruta local donde guardar el archivo
        
        Returns:
            True si se descargó exitosamente
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            return True
        
        except HttpError as error:
            raise Exception(f'Error al descargar archivo: {error}')
    
    def delete_file(self, file_id: str) -> bool:
        """
        Elimina un archivo de Google Drive.
        
        Args:
            file_id: ID del archivo a eliminar
        
        Returns:
            True si se eliminó exitosamente
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        
        except HttpError as error:
            raise Exception(f'Error al eliminar archivo: {error}')
    
    def get_file_info(self, file_id: str) -> dict:
        """
        Obtiene información detallada de un archivo.
        
        Args:
            file_id: ID del archivo
        
        Returns:
            Diccionario con metadatos del archivo
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, size, createdTime, modifiedTime, webViewLink, webContentLink, mimeType'
            ).execute()
            
            return file
        
        except HttpError as error:
            raise Exception(f'Error al obtener información del archivo: {error}')
    
    def list_files(self, page_size: int = 100) -> list:
        """
        Lista los archivos de la carpeta en Google Drive.
        
        Args:
            page_size: Número máximo de archivos a listar
        
        Returns:
            Lista de archivos con sus metadatos
        """
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, createdTime, size, webViewLink, mimeType)",
                orderBy="createdTime desc"
            ).execute()
            
            return results.get('files', [])
        
        except HttpError as error:
            raise Exception(f'Error al listar archivos: {error}')


# Instancia singleton del servicio
_drive_service_instance = None

def get_drive_service() -> GoogleDriveService:
    """
    Retorna una instancia singleton del servicio de Google Drive.
    """
    global _drive_service_instance
    if _drive_service_instance is None:
        _drive_service_instance = GoogleDriveService()
    return _drive_service_instance