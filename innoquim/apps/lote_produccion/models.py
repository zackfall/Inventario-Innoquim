from django.db import models, transaction
from django.conf import settings
from decimal import Decimal


class LoteProduccion(models.Model):
    """
    Lote de producción de productos terminados.
    
    Flujo:
    1. PENDING: Lote creado, se agregan materiales
    2. IN_PROGRESS: Se inicia producción (materiales se reservan)
    3. COMPLETED: Producción terminada (descuenta MP, suma producto, registra Kardex)
    4. CANCELLED: Lote cancelado (libera reservas si estaba en proceso)
    """
    
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("in_progress", "En Proceso"),
        ("completed", "Completado"),
        ("cancelled", "Cancelado"),
    )

    product = models.ForeignKey(
        "producto.Producto",
        on_delete=models.PROTECT,
        related_name="lotes_produccion",
        verbose_name="Producto a Fabricar"
    )
    
    batch_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código de Lote"
    )
    
    production_date = models.DateField(
        verbose_name="Fecha de Producción"
    )
    
    produced_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name="Cantidad Producida"
    )
    
    unit = models.ForeignKey(
        "unidad.Unidad",
        on_delete=models.PROTECT,
        related_name="lotes_produccion",
        verbose_name="Unidad de Medida"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Estado"
    )
    
    # NUEVO: Almacén donde se realiza la producción
    almacen = models.ForeignKey(
        "almacen.Almacen",
        on_delete=models.PROTECT,
        related_name="lotes_produccion",
        verbose_name="Almacén",
        help_text="Almacén donde se fabrica y se registra el inventario"
    )
    
    production_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lotes_gestionados",
        verbose_name="Responsable de Producción"
    )
    
    # NUEVO: Costos de producción
    costo_materiales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Costo de Materiales",
        help_text="Suma de costos de todas las materias primas usadas"
    )
    
    costo_unitario_producto = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name="Costo Unitario del Producto",
        help_text="costo_materiales / produced_quantity"
    )
    
    # NUEVO: Observaciones
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # NUEVO: Fecha de completado
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Completado"
    )

    class Meta:
        db_table = "lote_produccion"
        verbose_name = "Lote de Producción"
        verbose_name_plural = "Lotes de Producción"
        ordering = ["-production_date", "-created_at"]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['production_date']),
            models.Index(fields=['batch_code']),
        ]

    def __str__(self):
        return f"{self.batch_code} - {self.product.name} ({self.get_status_display()})"
    
    def calcular_costo_materiales(self):
        """
        Calcula el costo total de los materiales del lote.
        """
        from innoquim.apps.material_produccion.models import MaterialProduccion
        
        materiales = MaterialProduccion.objects.filter(batch=self)
        self.costo_materiales = sum(
            m.costo_total for m in materiales
        )
        
        if self.produced_quantity > 0:
            self.costo_unitario_producto = (
                self.costo_materiales / self.produced_quantity
            ).quantize(Decimal('0.0001'))
        
        self.save(update_fields=['costo_materiales', 'costo_unitario_producto'])
    
    @transaction.atomic
    def completar_produccion(self, usuario=None):
        """
        Completa el lote de producción:
        1. Valida que haya materiales
        2. Valida stock suficiente de materias primas
        3. Descuenta materias primas del inventario (Kardex SALIDA)
        4. Suma producto terminado al inventario (Kardex ENTRADA)
        5. Actualiza estado a COMPLETED
        
        Raises:
            ValueError: Si no hay materiales o stock insuficiente
        """
        from innoquim.apps.material_produccion.models import MaterialProduccion
        from innoquim.apps.inventario.models import Kardex
        from django.utils import timezone
        
        if self.status == 'completed':
            raise ValueError("Este lote ya fue completado")
        
        materiales = MaterialProduccion.objects.filter(batch=self)
        
        if not materiales.exists():
            raise ValueError("No se puede completar un lote sin materiales")
        
        # 1. Validar stock suficiente
        for material in materiales:
            saldo = Kardex.obtener_saldo_actual(
                almacen=self.almacen,
                item=material.raw_material
            )
            
            if saldo['cantidad'] < material.used_quantity:
                raise ValueError(
                    f"Stock insuficiente de {material.raw_material.nombre}. "
                    f"Requerido: {material.used_quantity}, "
                    f"Disponible: {saldo['cantidad']}"
                )
        
        # 2. Descontar materias primas (SALIDA)
        for material in materiales:
            Kardex.registrar_movimiento(
                almacen=self.almacen,
                item=material.raw_material,
                tipo_movimiento='SALIDA',
                motivo='PRODUCCION',
                cantidad=material.used_quantity,
                costo_unitario=material.costo_unitario,
                referencia_id=self.batch_code,
                observaciones=f"Usado en lote {self.batch_code}",
                usuario=usuario
            )
            
            # Actualizar stock en MateriaPrima
            material.raw_material.stock -= material.used_quantity
            material.raw_material.save(update_fields=['stock'])
        
        # 3. Calcular costos
        self.calcular_costo_materiales()
        
        # 4. Sumar producto terminado (ENTRADA)
        Kardex.registrar_movimiento(
            almacen=self.almacen,
            item=self.product,
            tipo_movimiento='ENTRADA',
            motivo='PRODUCCION',
            cantidad=self.produced_quantity,
            costo_unitario=self.costo_unitario_producto,
            referencia_id=self.batch_code,
            observaciones=f"Producción lote {self.batch_code}",
            usuario=usuario
        )
        
        # Actualizar stock en Producto
        self.product.stock += int(self.produced_quantity)
        self.product.save(update_fields=['stock'])
        
        # 5. Actualizar estado del lote
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        
        return True