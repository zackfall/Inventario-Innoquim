from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class Proveedor(models.Model):
    """
    Modelo para gestionar proveedores de INNO-QUIM.
    Empresas que suministran materias primas, envases e insumos.
    """
    
    # =================================================================
    # VALIDADORES 
    # =================================================================
    ruc_validator = RegexValidator(
        regex=r'^\d{13}$',
        message='El RUC debe tener exactamente 13 digitos'
    )
    
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='El numero de telefono debe tener entre 9 y 15 digitos'
    )
    # =================================================================
    # CAMPOS PRINCIPALES 
    # =================================================================
    # ID autoincremental con formato PR000001
    # Se genera automáticamente al guardar (ver método save())
    proveedor_id = models.CharField(
        max_length=8,
        unique=True,
        primary_key=True,
        editable=False,  # No editable manualmente
        verbose_name='ID Proveedor',
        help_text='Codigo unico del proveedor (ej: PR000001)'
    )
    
    # RUC: Campo obligatorio y único
    ruc = models.CharField(
        max_length=13,
        unique=True,
        null=False,
        blank=False,
        validators=[ruc_validator],
        verbose_name='RUC',
        help_text='Registro Unico de Contribuyentes (13 digitos)'
    )
    
    # Nombre de empresa: Campo obligatorio
    nombre_empresa = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name='Nombre de la Empresa',
        help_text='Razon social o nombre comercial del proveedor'
    )
    
    # Nombre de contacto: Campo opcional
    nombre_contacto = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Nombre de Contacto',
        help_text='Persona de contacto en la empresa proveedora'
    )
    
    # Teléfono: Campo opcional
    telefono = models.CharField(
        max_length=24,
        null=True,
        blank=True,
        validators=[phone_validator],
        verbose_name='Telefono',
        help_text='Numero de telefono principal de contacto'
    )
    
    # Email: Campo obligatorio con validación
    email = models.EmailField(
        max_length=100,
        null=False,
        blank=False,
        validators=[EmailValidator()],
        verbose_name='Correo Electronico',
        help_text='Email de contacto del proveedor'
    )
    
    # Dirección: Campo opcional
    direccion = models.TextField(
        null=True,
        blank=True,
        verbose_name='Direccion',
        help_text='Direccion fisica del proveedor'
    )
    
    # =================================================================
    # CAMPOS ADICIONALES 
    # =================================================================
    tipo_producto = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Tipo de Producto',
        help_text='Que productos o servicios provee (ej: Quimicos industriales, Envases)'
    )
    
    # =================================================================
    # CAMPOS DE AUDITORÍA 
    # =================================================================
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultima Actualizacion'
    )
    
    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['proveedor_id']
        
        # Indices para mejorar rendimiento en búsquedas
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['nombre_empresa']),
            models.Index(fields=['email']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para generar automáticamente
        el proveedor_id con formato PR000001, PR000002, etc.
        """
        if not self.proveedor_id:
            # Obtener el último proveedor registrado
            ultimo_proveedor = Proveedor.objects.all().order_by('proveedor_id').last()
            
            if ultimo_proveedor:
                # Extraer el número del último ID (PR000001 -> 1)
                ultimo_numero = int(ultimo_proveedor.proveedor_id[2:])
                nuevo_numero = ultimo_numero + 1
            else:
                # Si no hay proveedores, empezar desde 1
                nuevo_numero = 1
            
            # Formatear el nuevo ID: PR + número con 6 dígitos (PR000001)
            self.proveedor_id = f'PR{nuevo_numero:06d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.proveedor_id} - {self.nombre_empresa}"