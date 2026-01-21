"""
API REST para el gestor de archivos con Google Drive.
Servicio independiente que maneja únicamente la interacción con Google Drive.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

from google_drive_service import GoogleDriveService

# Cargar variables de entorno
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="Innoquim File Manager Service",
    description="Servicio de gestión de archivos con Google Drive",
    version="2.0.0"
)

# Configurar CORS - permitir acceso desde el backend Django
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Google Drive
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '/app/credentials/google-drive-credentials.json')
TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', '/app/credentials/token.json')
FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

if not FOLDER_ID:
    raise ValueError("GOOGLE_DRIVE_FOLDER_ID no está configurado")

# Inicializar servicio de Google Drive
drive_service = GoogleDriveService(CREDENTIALS_PATH, TOKEN_PATH, FOLDER_ID)

# Carpeta temporal
TEMP_DIR = "/app/temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


# =================================================================
# MODELOS DE DATOS
# =================================================================

class UploadResponse(BaseModel):
    """Modelo de respuesta al subir un archivo"""
    google_drive_id: str
    nombre: str
    url_descarga: str
    url_vista: str
    tamaño: int
    mime_type: str
    fecha_subida: str


class FileInfo(BaseModel):
    """Modelo de información de archivo"""
    id: str
    nombre: str
    tamaño: Optional[int] = None
    mime_type: Optional[str] = None
    fecha_creacion: Optional[str] = None
    url_descarga: Optional[str] = None
    url_vista: Optional[str] = None


class DeleteResponse(BaseModel):
    """Modelo de respuesta al eliminar"""
    success: bool
    message: str
    google_drive_id: str


# =================================================================
# ENDPOINTS
# =================================================================

@app.get("/")
async def root():
    """Endpoint raíz - Health check"""
    return {
        "service": "Innoquim File Manager",
        "status": "running",
        "version": "2.0.0",
        "description": "Servicio de gestión de archivos con Google Drive"
    }


@app.get("/health")
async def health_check():
    """Health check detallado"""
    try:
        # Verificar que las credenciales existan
        credentials_exist = os.path.exists(CREDENTIALS_PATH)
        token_exist = os.path.exists(TOKEN_PATH)
        
        return {
            "status": "healthy",
            "credentials_configured": credentials_exist,
            "token_configured": token_exist,
            "google_drive_folder_id": FOLDER_ID[:10] + "..." if FOLDER_ID else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Sube un archivo a Google Drive.
    
    Args:
        file: Archivo a subir
    
    Returns:
        Información del archivo subido en Google Drive
    """
    try:
        # Validar tamaño máximo (50 MB)
        max_size = 50 * 1024 * 1024
        file.file.seek(0, 2)  # Ir al final del archivo
        file_size = file.file.tell()
        file.file.seek(0)  # Volver al inicio
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo muy grande. Máximo permitido: 50 MB"
            )
        
        # Crear nombre temporal único
        file_extension = os.path.splitext(file.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Guardar archivo temporalmente
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Determinar MIME type
        mime_types = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.csv': 'text/csv',
        }
        mime_type = mime_types.get(file_extension.lower(), 'application/octet-stream')
        
        # Subir a Google Drive
        result = drive_service.upload_file(temp_path, file.filename)
        
        # Eliminar archivo temporal
        os.remove(temp_path)
        
        return UploadResponse(
            google_drive_id=result['id'],
            nombre=file.filename,
            url_descarga=result['webContentLink'],
            url_vista=result['webViewLink'],
            tamaño=file_size,
            mime_type=mime_type,
            fecha_subida=datetime.now().isoformat()
        )
    
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo: {str(e)}"
        )


@app.get("/api/files/{file_id}/info", response_model=FileInfo)
async def get_file_info(file_id: str):
    """
    Obtiene información de un archivo de Google Drive.
    
    Args:
        file_id: ID del archivo en Google Drive
    
    Returns:
        Información del archivo
    """
    try:
        file_info = drive_service.get_file_info(file_id)
        
        if not file_info:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado en Google Drive"
            )
        
        return FileInfo(
            id=file_info.get('id'),
            nombre=file_info.get('name'),
            tamaño=int(file_info.get('size', 0)),
            mime_type=file_info.get('mimeType'),
            fecha_creacion=file_info.get('createdTime'),
            url_descarga=file_info.get('webContentLink'),
            url_vista=file_info.get('webViewLink')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener información: {str(e)}"
        )


@app.delete("/api/files/{file_id}", response_model=DeleteResponse)
async def delete_file(file_id: str):
    """
    Elimina un archivo de Google Drive.
    
    Args:
        file_id: ID del archivo en Google Drive
    
    Returns:
        Confirmación de eliminación
    """
    try:
        success = drive_service.delete_file(file_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado o no se pudo eliminar"
            )
        
        return DeleteResponse(
            success=True,
            message="Archivo eliminado exitosamente de Google Drive",
            google_drive_id=file_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar archivo: {str(e)}"
        )


@app.get("/api/files")
async def list_files():
    """
    Lista todos los archivos de la carpeta en Google Drive.
    
    Returns:
        Lista de archivos
    """
    try:
        files = drive_service.list_files()
        
        return {
            "total": len(files),
            "archivos": [
                FileInfo(
                    id=f['id'],
                    nombre=f['name'],
                    tamaño=int(f.get('size', 0)),
                    fecha_creacion=f.get('createdTime'),
                    url_vista=f.get('webViewLink')
                )
                for f in files
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar archivos: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)