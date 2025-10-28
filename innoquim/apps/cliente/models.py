from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class Cliente(models.Model):
    """
    Modelo para gestionar los clientes empresariales de INNO-QUIM.
    
    Notas importantes:
    - cliente_id se autogenera con formato CL000001 (ver metodo save())
    - El RUC debe ser unico y tener exactamente 13 digitos (Ecuador)
    - nombre_contacto es opcional ya que algunos clientes solo proporcionan email
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
    
    # cliente_id: PRIMARY KEY autogenerada
    # Formato: CL + 6 digitos (ej: CL000001, CL000002, ...)
    cliente_id = models.CharField(
        max_length=8,
        primary_key=True,
        editable=False,
        verbose_name='ID Cliente',
        help_text='Codigo unico autogenerado (formato: CL000001)'
    )
    
    ruc = models.CharField(
        max_length=13,
        unique=True,
        validators=[ruc_validator],
        verbose_name='RUC'
    )
    
    nombre_empresa = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Empresa'
    )
    
    nombre_contacto = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Nombre del Contacto',
        help_text='Nombre de la persona de contacto en la empresa (opcional)'
    )
    
    telefono = models.CharField(
        max_length=24,
        blank=True,
        null=True,
        validators=[phone_validator],
        verbose_name='Telefono'
    )
    
    email = models.EmailField(
        max_length=100,
        validators=[EmailValidator()],
        verbose_name='Correo Electronico'
    )
    
    direccion = models.TextField(
        verbose_name='Direccion'
    )
    
    # =================================================================
    # CAMPOS DE AUDITORIA (automaticos)
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
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['cliente_id']
        
        indexes = [
            models.Index(fields=['ruc']),
            models.Index(fields=['nombre_empresa']),
        ]
    
    def __str__(self):
        return f"{self.cliente_id} - {self.nombre_empresa}"
    
    def save(self, *args, **kwargs):
        """
        Override del metodo save() para autogenerar cliente_id.
        Formato: CL + 6 digitos (CL000001, CL000002, ...)
        """
        if not self.cliente_id:
            last_cliente = Cliente.objects.order_by('-cliente_id').first()
            
            if last_cliente and last_cliente.cliente_id:
                last_number = int(last_cliente.cliente_id[2:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.cliente_id = f"CL{new_number:06d}"
        
        super().save(*args, **kwargs)