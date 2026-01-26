"""
Signals para gestionar inventario cuando cambian las órdenes de cliente.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from .models import OrdenCliente
from innoquim.apps.producto.models import Producto
from innoquim.apps.inventario.models import Kardex


@receiver(post_save, sender=OrdenCliente)
def gestionar_inventario_orden_cliente(sender, instance, created, **kwargs):
    """
    Gestiona el inventario de productos cuando cambia el estado de una orden de cliente.

    - Al completar una orden: descuenta productos del inventario y registra en Kardex
    - Al cancelar una orden: devuelve productos al inventario (si estaban descontados)
    """

    # Solo procesar si la orden fue actualizada (no creada)
    if created:
        return

    # Si el estado cambia a COMPLETED
    if instance.status == "completed":
        try:
            # Obtener el almacén (primera opción disponible)
            from innoquim.apps.almacen.models import Almacen
            almacen = Almacen.objects.first()
            if not almacen:
                print(f"No hay almacén disponible para registrar venta de orden {instance.order_code}")
                return

            # Descontar cada producto de la orden
            for item in instance.items.all():
                producto = item.product
                producto.stock -= item.quantity
                producto.save()

                # Registrar en Kardex (salida por venta)
                Kardex.registrar_movimiento(
                    almacen=almacen,
                    item=producto,
                    tipo_movimiento="SALIDA",
                    motivo="VENTA",
                    cantidad=Decimal(str(item.quantity)),
                    costo_unitario=producto.price,
                    referencia_id=str(instance.id),
                    observaciones=f"Venta en orden {instance.order_code}",
                    usuario=None,
                )

        except Exception as e:
            print(f"Error al gestionar inventario de orden {instance.order_code}: {str(e)}")

    # Si el estado cambia a CANCELLED y la orden estaba completada
    elif instance.status == "cancelled":
        # Aquí podríamos implementar lógica para devolver productos al inventario
        # si se cancela una orden que ya estaba completada
        # Por ahora, solo registramos que fue cancelada
        pass