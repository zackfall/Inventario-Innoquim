from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps


class OrdenItem(models.Model):
    """
    Modelo para gestionar items individuales de ordenes de clientes.
    Representa cada producto incluido en una OrdenCliente con su cantidad y subtotal.
    
    Relaciones:
    - order: FK a tabla orden_cliente (orden a la que pertenece el item)
    - product: FK a tabla producto (producto solicitado)
    - unit: FK a tabla unidad (unidad de medida del producto)
    
    Notas:
    - subtotal se calcula automaticamente en save() (quantity * product.price)
    - Las señales post_save y post_delete actualizan los totales de la orden padre
    - unit se obtiene automaticamente del producto asociado
    """
    
    # =================================================================
    # RELACIONES (FOREIGN KEYS)
    # =================================================================
    
    # order: FK a tabla orden_cliente
    # on_delete=CASCADE: si se borra la orden, se borran todos sus items
    # related_name="items": acceso inverso desde OrdenCliente.items.all()
    order = models.ForeignKey(
        "orden_cliente.OrdenCliente",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Orden",
        help_text="Orden a la que pertenece este item"
    )
    
    # product: FK a tabla producto
    # on_delete=PROTECT: no permite borrar producto si tiene items asociados
    # Razon: protege la integridad de datos historicos de ordenes
    product = models.ForeignKey(
        "producto.Producto",
        on_delete=models.PROTECT,
        related_name="orden_items",
        verbose_name="Producto",
        help_text="Producto solicitado en este item"
    )
    
    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================
    
    # quantity: Cantidad entera de envases solicitados
    # PositiveIntegerField: solo acepta numeros enteros positivos
    quantity = models.PositiveIntegerField(
        verbose_name="Cantidad",
        help_text="Cantidad de envases del producto"
    )
    
    # unit: FK a tabla unidad
    # Se obtiene automaticamente del producto asociado
    # on_delete=PROTECT: no permite borrar unidad si tiene items asociados
    unit = models.ForeignKey(
        "unidad.Unidad",
        on_delete=models.PROTECT,
        related_name="orden_items",
        verbose_name="Unidad de Medida",
        help_text="Unidad de medida del producto (se hereda del producto)"
    )

    # =================================================================
    # CAMPOS CALCULADOS (SNAPSHOT)
    # =================================================================
    
    # subtotal: Snapshot del calculo quantity * product.price
    # Se calcula automaticamente en save()
    # Formato: hasta 12 digitos totales, 2 decimales (ej: 9999999999.99)
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Subtotal",
        help_text="Subtotal del item (quantity * precio, autocalculado)"
    )

    # =================================================================
    # CAMPOS DE AUDITORIA (automaticos)
    # =================================================================
    
    # auto_now_add=True: se llena SOLO al crear el registro
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creacion"
    )
    
    # auto_now=True: se actualiza CADA VEZ que se modifica el registro
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ultima Actualizacion"
    )

    class Meta:
        db_table = "orden_item"
        verbose_name = "Orden Item"
        verbose_name_plural = "Orden Items"
        ordering = ["-created_at"]  # Items mas recientes primero

    def __str__(self):
        """Representacion legible del objeto (usado en admin y logs)"""
        order_id = self.order.id if self.order_id else "N/A"
        product_name = self.product.name if self.product_id else "N/A"
        return f"Item {self.id or '-'} - Order {order_id} - {product_name}"

    def save(self, *args, **kwargs):
        """
        Override del metodo save() para calcular subtotal automaticamente.
        
        Logica:
        1. Obtiene el precio del producto (snapshot en el momento de la orden)
        2. Calcula subtotal = quantity * precio
        3. Redondea a 2 decimales usando ROUND_HALF_UP (redondeo comercial)
        4. Guarda el registro
        
        IMPORTANTE: Usa precio del producto como snapshot, no se actualiza
        si el precio del producto cambia posteriormente
        """
        try:
            # Obtener precio del producto como snapshot
            price = self.product.price or Decimal("0.00")
        except Exception:
            # Si hay error al obtener precio, usar 0.00
            price = Decimal("0.00")
        
        # Calcular subtotal: quantity * precio
        # quantize(): redondea a 2 decimales con redondeo comercial
        self.subtotal = (Decimal(self.quantity) * price).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
        
        # Guardar el registro normalmente
        super().save(*args, **kwargs)


# =================================================================
# SEÑALES PARA MANTENER TOTALES DE ORDEN SINCRONIZADOS
# =================================================================

@receiver(post_save, sender=OrdenItem)
def orden_item_saved(sender, instance, **kwargs):
    """
    Señal post_save: actualiza totales de la orden cuando se crea/modifica un item.
    
    Se ejecuta despues de:
    - Crear un nuevo item
    - Modificar un item existente
    
    Accion: recalcula tax_amount y total_amount de la orden padre
    """
    if instance.order_id:
        # Importar modelo dinamicamente para evitar importacion circular
        OrdenCliente = apps.get_model("orden_cliente", "OrdenCliente")
        orden = OrdenCliente.objects.filter(pk=instance.order_id).first()
        if orden:
            # Recalcular totales de la orden
            orden.update_totals()


@receiver(post_delete, sender=OrdenItem)
def orden_item_deleted(sender, instance, **kwargs):
    """
    Señal post_delete: actualiza totales de la orden cuando se elimina un item.
    
    Se ejecuta despues de:
    - Eliminar un item existente
    
    Accion: recalcula tax_amount y total_amount de la orden padre
    """
    if not instance.order_id:
        return
    
    # Importar modelo dinamicamente para evitar importacion circular
    OrdenCliente = apps.get_model("orden_cliente", "OrdenCliente")
    orden = OrdenCliente.objects.filter(pk=instance.order_id).first()
    if orden:
        # Recalcular totales de la orden
        orden.update_totals()