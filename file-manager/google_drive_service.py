"""
Servicio para interactuar con Google Drive API usando OAuth 2.0.
Compatible con cuentas personales de Google.
"""

import io
import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """
    Clase para gestionar archivos en Google Drive usando OAuth 2.0.
    Compatible con cuentas personales de Google.
    """

    # Scope necesario para crear y gestionar archivos
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self, credentials_path: str, token_path: str, folder_id: str):
        """
        Inicializa el servicio de Google Drive con OAuth 2.0.

        Args:
            credentials_path: Ruta al archivo JSON de credenciales OAuth 2.0
            token_path: Ruta donde se guardará el token de autenticación
            folder_id: ID de la carpeta en Google Drive
        """
        self.folder_id = folder_id
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        self.service = None

        self._authenticate()

    def _authenticate(self):
        """
        Autentica con Google Drive usando OAuth 2.0.
        ✅ VERSIÓN MEJORADA para servidor
        """
        creds = None

        # El token.json almacena los tokens de acceso y actualización
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, self.SCOPES
                )
            except Exception as e:
                logger.warning(f"Error al cargar token existente: {e}")
                creds = None

        # Si no hay credenciales válidas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    # Refrescar token expirado
                    creds.refresh(Request())
                    logger.info("Token refrescado exitosamente")
                except Exception as e:
                    logger.error(f"Error al refrescar token: {e}")
                    creds = None

            # ❌ NO usar run_local_server en servidor
            # Si llegamos aquí, necesitamos autenticación manual
            if not creds:
                error_msg = (
                    "Autenticación requerida. "
                    "Usa el endpoint /api/auth/url para obtener la URL de autorización."
                )
                logger.error(error_msg)
                raise Exception(error_msg)

            # Guardar credenciales
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.credentials = creds
        if creds:
            self.service = build("drive", "v3", credentials=self.credentials)
            logger.info("Autenticación con Google Drive exitosa")
        else:
            self.service = None
            logger.warning("No se pudieron establecer las credenciales de Google Drive")

    def upload_file(self, file_path: str, file_name: str) -> dict:
        """
        Sube un archivo a Google Drive.

        Args:
            file_path: Ruta local del archivo a subir
            file_name: Nombre que tendrá el archivo en Drive

        Returns:
            dict con 'id', 'webViewLink' y 'webContentLink'
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
            
        try:
            file_metadata = {"name": file_name, "parents": [self.folder_id]}

            media = MediaFileUpload(file_path, resumable=True)

            file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, webViewLink, webContentLink",
                )
                .execute()
            )

            # Hacer el archivo público
            self.service.permissions().create(
                fileId=file.get("id"), body={"type": "anyone", "role": "reader"}
            ).execute()

            return {
                "id": file.get("id"),
                "webViewLink": file.get("webViewLink"),
                "webContentLink": file.get("webContentLink"),
            }

        except HttpError as error:
            logger.error(f"Error al subir archivo: {error}")
            raise

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """
        Descarga un archivo de Google Drive.

        Args:
            file_id: ID del archivo en Google Drive
            destination_path: Ruta local donde guardar el archivo

        Returns:
            True si se descargó exitosamente
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
            
        try:
            request = self.service.files().get_media(fileId=file_id)

            with io.FileIO(destination_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    logger.info(f"Descarga {int(status.progress() * 100)}%")

            return True

        except HttpError as error:
            logger.error(f"Error al descargar archivo: {error}")
            raise

    def list_files(self, page_size: int = 100) -> list:
        """
        Lista los archivos de la carpeta en Google Drive.

        Args:
            page_size: Número máximo de archivos a listar

        Returns:
            Lista de archivos con sus metadatos
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
            
        try:
            query = f"'{self.folder_id}' in parents and trashed=false"

            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    fields="files(id, name, createdTime, size, webViewLink)",
                )
                .execute()
            )

            return results.get("files", [])

        except HttpError as error:
            logger.error(f"Error al listar archivos: {error}")
            return []

    def delete_file(self, file_id: str) -> bool:
        """
        Elimina PERMANENTEMENTE un archivo de Google Drive.

        Args:
            file_id: ID del archivo a eliminar

        Returns:
            True si se eliminó exitosamente

        Raises:
            HttpError: Si hay un error al eliminar (404, 403, etc.)
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
            
        try:
            # Verificar que el archivo existe antes de intentar eliminarlo
            try:
                self.service.files().get(fileId=file_id, fields="id").execute()
            except HttpError as e:
                if e.resp.status == 404:
                    logger.warning(f"Archivo {file_id} no encontrado en Google Drive")
                    raise ValueError(f"Archivo no encontrado: {file_id}")
                raise

            # Eliminar el archivo permanentemente
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Archivo {file_id} eliminado exitosamente de Google Drive")
            return True

        except HttpError as error:
            logger.error(f"Error HTTP al eliminar archivo {file_id}: {error}")
            # Re-lanzar la excepción para que FastAPI la maneje
            raise
        except Exception as error:
            logger.error(f"Error inesperado al eliminar archivo {file_id}: {error}")
            raise

    def get_file_info(self, file_id: str) -> dict:
        """
        Obtiene información de un archivo.

        Args:
            file_id: ID del archivo

        Returns:
            Diccionario con metadatos del archivo
        """
        if not self.service:
            raise Exception("Servicio de Google Drive no inicializado")
            
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, size, createdTime, modifiedTime, webViewLink, webContentLink, mimeType",
                )
                .execute()
            )

            return file

        except HttpError as error:
            logger.error(f"Error al obtener info del archivo: {error}")
            raise

