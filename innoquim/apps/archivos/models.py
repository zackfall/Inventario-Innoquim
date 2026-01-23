from django.db import models
from django.conf import settings


class Archivo(models.Model):
    """
    Modelo para gestionar archivos PDF almacenados en Google Drive.
    
    Flujo:
    1. Frontend genera PDF con jsPDF
    2. Frontend envia PDF al backend via API
    3. Backend sube PDF a Google Drive
    4. Backend guarda metadatos aqui
    5. Frontend puede listar y descargar PDFs guardados
    
    Relaciones:
    - usuario_generador: quien subio el archivo
    
    Notas:
    - google_drive_id: ID del archivo en Google Drive
    - url_descarga: URL directa para descargar desde Drive
    - El archivo fisico esta en Google Drive, NO en el servidor
    """
    
    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================
    
    # archivo_id: PRIMARY KEY autogenerada
    # Formato: ARC + 6 digitos (ej: ARC000001, ARC000002, ...)
    archivo_id = models.CharField(
        max_length=9,
        primary_key=True,
        editable=False,
        verbose_name='ID Archivo',
        help_text='Codigo unico autogenerado (formato: ARC000001)'
    )
    
    # nombre: nombre del archivo PDF
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Archivo',
        help_text='Nombre descriptivo del PDF (ej: Reporte_Inventario_2025-11-15.pdf)'
    )
    
    # tipo_reporte: categoria del reporte
    tipo_reporte = models.CharField(
        max_length=30,
        verbose_name='Tipo de Reporte',
        help_text='Categoria del reporte generado'
    )
    
    # =================================================================
    # RELACION CON GOOGLE DRIVE
    # =================================================================
    
    # google_drive_id: ID del archivo en Google Drive
    # Este ID se usa para acceder al archivo via API de Google Drive
    google_drive_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Google Drive ID',
        help_text='ID del archivo en Google Drive'
    )
    
    # url_descarga: URL directa para descargar el archivo
    url_descarga = models.URLField(
        max_length=500,
        verbose_name='URL de Descarga',
        help_text='URL directa para descargar el archivo desde Google Drive'
    )
    
    # =================================================================
    # METADATOS DEL ARCHIVO
    # =================================================================
    
    # tamaño: tamaño del archivo en bytes
    tamaño = models.BigIntegerField(
        verbose_name='Tamaño',
        help_text='Tamaño del archivo en bytes'
    )
    
    # descripcion: descripcion opcional del reporte
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripcion',
        help_text='Descripcion opcional del contenido del reporte'
    )
    
    # =================================================================
    # USUARIO Y AUDITORIA
    # =================================================================
    
    # usuario_generador: quien subio/genero el archivo
    # on_delete=SET_NULL: si se borra el usuario, el archivo permanece
    usuario_generador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='archivos_generados',
        verbose_name='Usuario Generador',
        help_text='Usuario que subio el archivo'
    )
    
    # fecha_generacion: cuando se subio el archivo
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Generacion'
    )
    
    # fecha_actualizacion: ultima modificacion del registro
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultima Actualizacion'
    )
    
    class Meta:
        db_table = 'archivo'
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        ordering = ['-fecha_generacion']
        
        # Indices para optimizar consultas
        indexes = [
            models.Index(fields=['tipo_reporte']),
            models.Index(fields=['fecha_generacion']),
            models.Index(fields=['usuario_generador']),
        ]
    
    def __str__(self):
        return f"{self.archivo_id} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Override del metodo save() para autogenerar archivo_id.
        Formato: ARC + 6 digitos (ARC000001, ARC000002, ...)
        """
        if not self.archivo_id:
            last_archivo = Archivo.objects.order_by('-archivo_id').first()
            
            if last_archivo and last_archivo.archivo_id:
                last_number = int(last_archivo.archivo_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.archivo_id = f"ARC{new_number:06d}"
        
        super().save(*args, **kwargs)
    
    def get_tamaño_legible(self):
        """
        Retorna el tamaño del archivo en formato legible.
        Ejemplo: 1024 bytes -> "1.0 KB"
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.tamaño < 1024.0:
                return f"{self.tamaño:.1f} {unit}"
            self.tamaño /= 1024.0
        return f"{self.tamaño:.1f} TB"