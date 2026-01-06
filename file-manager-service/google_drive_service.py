"""
Servicio para interactuar con Google Drive API.
Permite subir, descargar, listar y eliminar archivos.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io


class GoogleDriveService:
    """
    Clase para gestionar archivos en Google Drive.
    
    Uso:
    - Subir archivos PDF
    - Descargar archivos
    - Listar archivos de la carpeta
    - Eliminar archivos
    """
    
    def __init__(self, credentials_path: str, folder_id: str):
        """
        Inicializa el servicio de Google Drive.
        
        Args:
            credentials_path: Ruta al archivo JSON de credenciales
            folder_id: ID de la carpeta en Google Drive donde se guardan los PDFs
        """
        self.folder_id = folder_id
        
        # Escopos necesarios para Google Drive API
        # 'drive.file': permite crear y gestionar archivos
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        # Autenticar con Service Account
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )
        
        # Crear cliente de Google Drive API
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    def upload_file(self, file_path: str, file_name: str) -> dict:
        """
        Sube un archivo a Google Drive.
        
        Args:
            file_path: Ruta local del archivo a subir
            file_name: Nombre que tendra el archivo en Drive
        
        Returns:
            dict con 'id' (ID del archivo en Drive) y 'webViewLink' (URL)
        """
        try:
            # Metadatos del archivo
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]  # Subir a la carpeta especifica
            }
            
            # Subir archivo
            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Hacer el archivo publico para poder descargarlo
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
            print(f'Error al subir archivo: {error}')
            raise
    
    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Descarga un archivo de Google Drive.
        
        Args:
            file_id: ID del archivo en Google Drive
            destination_path: Ruta local donde guardar el archivo
        
        Returns:
            True si se descargo exitosamente, False si hubo error
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            with io.FileIO(destination_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Descarga {int(status.progress() * 100)}%")
            
            return True
        
        except HttpError as error:
            print(f'Error al descargar archivo: {error}')
            return False
    
    def list_files(self, page_size: int = 100) -> list:
        """
        Lista los archivos de la carpeta en Google Drive.
        
        Args:
            page_size: Numero maximo de archivos a listar
        
        Returns:
            Lista de archivos con sus metadatos
        """
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, createdTime, size, webViewLink)"
            ).execute()
            
            return results.get('files', [])
        
        except HttpError as error:
            print(f'Error al listar archivos: {error}')
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """
        Elimina un archivo de Google Drive.
        
        Args:
            file_id: ID del archivo a eliminar
        
        Returns:
            True si se elimino exitosamente, False si hubo error
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        
        except HttpError as error:
            print(f'Error al eliminar archivo: {error}')
            return False
    
    def get_file_info(self, file_id: str) -> dict:
        """
        Obtiene informacion de un archivo.
        
        Args:
            file_id: ID del archivo
        
        Returns:
            Diccionario con metadatos del archivo
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, size, createdTime, modifiedTime, webViewLink, webContentLink'
            ).execute()
            
            return file
        
        except HttpError as error:
            print(f'Error al obtener info del archivo: {error}')
            return {}