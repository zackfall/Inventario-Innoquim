from django.db import models
from innoquim.apps.materia_prima.models import MateriaPrima
from innoquim.apps.almacen.models import Almacen
from innoquim.apps.unidad.models import Unidad


class InventarioMaterial(models.Model):
    """
    Control de cantidades actuales de materias primas en almacenes.
    Representa el stock disponible en cada ubicacion.
    
    Relaciones:
    - materia_prima_id: QUE material es
    - almacen_id: DONDE esta guardado
    - unidad_id: EN QUE se mide (kg, litros, etc)
    
    Notas:
    - Este modelo solo refleja el stock ACTUAL
    - El historial de compras (con proveedor) esta en recepcion_material
    - La cantidad se actualiza con recepciones (+) y consumos (-)
    - unique_together evita duplicados (mismo material en mismo almacen)
    """
    
    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================
    
    # inventario_material_id: PRIMARY KEY autogenerada
    # Formato: IM + 6 digitos (ej: IM000001, IM000002, ...)
    # Se genera automaticamente en save() basandose en el ultimo registro
    inventario_material_id = models.CharField(
        max_length=8,  # IM (2) + 6 digitos = 8 caracteres max
        primary_key=True,
        editable=False,
        verbose_name='ID Inventario Material',
        help_text='Codigo unico autogenerado (formato: IM000001)'
    )
    
    # =================================================================
    # RELACIONES (FOREIGN KEYS)
    # =================================================================
    
    # materia_prima_id: QUE material se esta inventariando
    # on_delete=PROTECT: no permite borrar materia prima si tiene inventario
    # Razon: protege la integridad (evita perder referencia del material)
    materia_prima_id = models.ForeignKey(
        MateriaPrima,
        on_delete=models.PROTECT,
        verbose_name='Materia Prima',
        help_text='Material que se esta inventariando'
    )
    
    # almacen_id: DONDE esta guardado el material
    # on_delete=PROTECT: no permite borrar almacen si tiene inventario
    # Razon: protege datos (no puedes eliminar un almacen con stock)
    almacen_id = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        verbose_name='Almacen',
        help_text='Ubicacion fisica donde esta el material'
    )
    
    # unidad_id: EN QUE unidad se mide
    # on_delete=PROTECT: no permite borrar unidad si tiene inventario
    # Debe coincidir con la unidad de la materia prima
    unidad_id = models.ForeignKey(
        Unidad,
        on_delete=models.PROTECT,
        verbose_name='Unidad de Medida',
        help_text='Unidad en que se mide la cantidad (kg, litros, etc)'
    )
    
    # =================================================================
    # CANTIDAD EN STOCK
    # =================================================================
    
    # cantidad: stock actual disponible
    # Se actualiza con: recepciones (+) y consumos por produccion (-)
    # max_digits=10, decimal_places=2: permite valores como 99999999.99
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Disponible',
        help_text='Cantidad actual en stock'
    )
    
    # =================================================================
    # CAMPOS DE AUDITORIA (automaticos)
    # =================================================================
    
    # auto_now_add=True: se llena SOLO al crear el registro
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creacion'
    )
    
    # auto_now=True: se actualiza CADA VEZ que se modifica el registro
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultima Actualizacion'
    )
    
    class Meta:
        db_table = 'inventario_material'
        verbose_name = 'Inventario de Material'
        verbose_name_plural = 'Inventarios de Materiales'
        ordering = ['inventario_material_id']
        
        # unique_together: restriccion de unicidad compuesta
        # NO puede haber dos registros con la misma combinacion
        # Un material solo puede estar UNA VEZ en cada almacen
        unique_together = [['materia_prima_id', 'almacen_id']]
        
        # Indices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['materia_prima_id']),
            models.Index(fields=['almacen_id']),
        ]
    
    def __str__(self):
        """Representacion legible del objeto (usado en admin y logs)"""
        return f"{self.inventario_material_id} - {self.materia_prima_id.nombre} ({self.cantidad} {self.unidad_id.simbolo})"
    
    def save(self, *args, **kwargs):
        """
        Override del metodo save() para autogenerar inventario_material_id.
        
        Logica:
        1. Si es un registro nuevo (no tiene inventario_material_id)
        2. Busca el ultimo inventario_material_id en la BD
        3. Extrae el numero, suma 1
        4. Formatea con padding de 6 digitos
        
        Formato: IM + 6 digitos (IM000001, IM000002, ...)
        Soporta hasta 999,999 registros
        """
        if not self.inventario_material_id:
            # Obtener el ultimo inventario ordenado descendente
            last_inventario = InventarioMaterial.objects.order_by('-inventario_material_id').first()
            
            if last_inventario and last_inventario.inventario_material_id:
                # Extraer numero del formato IM000001 -> 1
                # [2:] elimina los primeros 2 caracteres "IM"
                last_number = int(last_inventario.inventario_material_id[2:])
                new_number = last_number + 1
            else:
                # Primera insercion en la tabla
                new_number = 1
            
            # f-string con formato :06d = padding de 6 digitos con ceros
            self.inventario_material_id = f"IM{new_number:06d}"
        
        # Llamar al save() original de Django
        super().save(*args, **kwargs)