"""
API REST para el gestor de archivos.
Permite subir, descargar, listar y eliminar archivos PDF en Google Drive.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
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
    description="Servicio de gestion de archivos PDF con Google Drive",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicio de Google Drive
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-drive-credentials.json')
FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

if not FOLDER_ID:
    raise ValueError("GOOGLE_DRIVE_FOLDER_ID no esta configurado en .env")

drive_service = GoogleDriveService(CREDENTIALS_PATH, FOLDER_ID)

# Carpeta temporal para guardar archivos antes de subirlos
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


# =================================================================
# MODELOS DE DATOS
# =================================================================

class ArchivoResponse(BaseModel):
    """Modelo de respuesta al subir un archivo"""
    archivo_id: str
    nombre: str
    google_drive_id: str
    url_descarga: str
    tamaño: int
    fecha_subida: str


class ArchivoInfo(BaseModel):
    """Modelo de informacion de archivo"""
    id: str
    nombre: str
    tamaño: Optional[int] = None
    fecha_creacion: Optional[str] = None
    url_descarga: Optional[str] = None


# =================================================================
# ENDPOINTS
# =================================================================

@app.get("/")
async def root():
    """Endpoint raiz para verificar que el servicio esta funcionando"""
    return {
        "service": "Innoquim File Manager",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}


@app.post("/api/archivos/upload", response_model=ArchivoResponse)
async def upload_file(
    file: UploadFile = File(...),
    tipo_reporte: str = Form(...),
    descripcion: Optional[str] = Form(None)
):
    """
    Sube un archivo PDF a Google Drive.
    
    Args:
        file: Archivo PDF a subir
        tipo_reporte: Tipo de reporte (inventario, clientes, etc)
        descripcion: Descripcion opcional del reporte
    
    Returns:
        Informacion del archivo subido
    """
    # Validar que sea un PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    try:
        # Generar nombre unico para el archivo temporal
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Guardar archivo temporalmente
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Subir a Google Drive
        result = drive_service.upload_file(temp_path, file.filename)
        
        # Eliminar archivo temporal
        os.remove(temp_path)
        
        # Preparar respuesta
        return ArchivoResponse(
            archivo_id=result['id'],
            nombre=file.filename,
            google_drive_id=result['id'],
            url_descarga=result['webContentLink'],
            tamaño=len(content),
            fecha_subida=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {str(e)}")


@app.get("/api/archivos/list")
async def list_files():
    """
    Lista todos los archivos en Google Drive.
    
    Returns:
        Lista de archivos con sus metadatos
    """
    try:
        files = drive_service.list_files()
        
        return {
            "total": len(files),
            "archivos": [
                ArchivoInfo(
                    id=f['id'],
                    nombre=f['name'],
                    tamaño=int(f.get('size', 0)),
                    fecha_creacion=f.get('createdTime'),
                    url_descarga=f.get('webViewLink')
                )
                for f in files
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar archivos: {str(e)}")


@app.get("/api/archivos/{file_id}/info")
async def get_file_info(file_id: str):
    """
    Obtiene informacion detallada de un archivo.
    
    Args:
        file_id: ID del archivo en Google Drive
    
    Returns:
        Informacion del archivo
    """
    try:
        file_info = drive_service.get_file_info(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        return file_info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener info: {str(e)}")


@app.delete("/api/archivos/{file_id}")
async def delete_file(file_id: str):
    """
    Elimina un archivo de Google Drive.
    
    Args:
        file_id: ID del archivo a eliminar
    
    Returns:
        Confirmacion de eliminacion
    """
    try:
        success = drive_service.delete_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Archivo no encontrado o error al eliminar")
        
        return {"message": "Archivo eliminado exitosamente", "file_id": file_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)