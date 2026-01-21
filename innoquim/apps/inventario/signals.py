"""
Signals para integrar automáticamente el Kardex con otros módulos.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


@receiver(post_save, sender="recepcion_material.RecepcionMaterial")
def recepcion_material_saved(sender, instance, created, **kwargs):
    """
    Cuando se crea una RecepcionMaterial, registra ENTRADA en Kardex.
    
    Este signal permite que RecepcionMaterial funcione independientemente de RecepcionItem,
    dando flexibilidad al sistema para recibir material de dos formas:
    1. Recepción simple (directamente en RecepcionMaterial)
    2. Recepción detallada (usando RecepcionItem)
    """
    if created and instance.materia_prima and instance.cantidad and instance.costo_unitario:
        from innoquim.apps.inventario.models import Kardex
        
        # Registrar movimiento en Kardex
        Kardex.registrar_movimiento(
            almacen=instance.almacen,
            item=instance.materia_prima,
            tipo_movimiento="ENTRADA",
            motivo="COMPRA",
            cantidad=Decimal(str(instance.cantidad)),
            costo_unitario=Decimal(str(instance.costo_unitario)),
            referencia_id=f"RM{instance.id}-DIRECT",
            observaciones=f"Recepción directa - Factura: {instance.numero_de_factura or 'N/A'} - Proveedor: {instance.proveedor}",
            usuario=None,
        )
        
        # Actualizar InventarioMaterial
        actualizar_inventario_material(instance.materia_prima, instance.almacen)


@receiver(post_save, sender="recepcion_item.RecepcionItem")
def recepcion_item_saved(sender, instance, created, **kwargs):
    """
    Cuando se crea un RecepcionItem, registra ENTRADA en Kardex.

    Flujo:
    1. Se recibe material de proveedor (RecepcionItem creado)
    2. Se registra automáticamente como ENTRADA en Kardex
    3. Se actualiza el costo promedio de la materia prima
    4. Se actualiza el saldo en inventario
    """
    if created:  # Solo cuando se crea, no cuando se actualiza
        from innoquim.apps.inventario.models import Kardex

        # Obtener datos necesarios
        recepcion = instance.id_recepcion_material
        almacen = recepcion.almacen
        materia_prima = instance.materia_prima
        cantidad = Decimal(str(instance.cantidad))
        precio_compra = instance.precio_compra or Decimal("0.00")

        # Registrar movimiento en Kardex
        Kardex.registrar_movimiento(
            almacen=almacen,
            item=materia_prima,
            tipo_movimiento="ENTRADA",
            motivo="COMPRA",
            cantidad=cantidad,
            costo_unitario=precio_compra,
            referencia_id=f"RM{recepcion.id}-ITEM{instance.id}",
            observaciones=f"Recepción de material - Lote: {instance.lote}",
            usuario=None,  # Puedes agregar el usuario si está disponible
        )

        # Actualizar InventarioMaterial
        actualizar_inventario_material(materia_prima, almacen)


@receiver(post_save, sender="material_produccion.MaterialProduccion")
def material_produccion_saved(sender, instance, created, **kwargs):
    """
    Cuando se consume material en producción, registra SALIDA en Kardex.

    Flujo:
    1. Se crea un lote de producción y se registran materiales usados
    2. Se registra automáticamente como SALIDA en Kardex
    3. Se reduce el inventario de materias primas
    """
    if created:  # Solo cuando se crea
        from innoquim.apps.inventario.models import Kardex

        # Obtener datos necesarios
        lote = instance.batch
        materia_prima = instance.raw_material
        cantidad = Decimal(str(instance.used_quantity))

        # Obtener el costo promedio actual de la materia prima
        costo_promedio = materia_prima.costo_promedio or Decimal("0.00")

        # Por ahora usamos un almacén por defecto
        # TODO: Agregar campo de almacén en MaterialProduccion
        from innoquim.apps.almacen.models import Almacen

        almacen = Almacen.objects.first()  # Usar primer almacén

        if almacen:
            # Registrar movimiento en Kardex
            Kardex.registrar_movimiento(
                almacen=almacen,
                item=materia_prima,
                tipo_movimiento="SALIDA",
                motivo="PRODUCCION",
                cantidad=cantidad,
                costo_unitario=costo_promedio,
                referencia_id=f"LOTE{lote.id}-MAT{instance.id}",
                observaciones=f"Consumo en producción - Lote: {lote.batch_code}",
                usuario=None,
            )

            # Actualizar InventarioMaterial
            actualizar_inventario_material(materia_prima, almacen)


@receiver(post_save, sender="orden_item.OrdenItem")
def orden_item_saved(sender, instance, created, **kwargs):
    """
    Cuando se despacha un producto, registra SALIDA en Kardex.

    NOTA: Este signal solo debe activarse cuando el estado de la orden
    cambia a "completada". Por ahora lo dejamos comentado.
    """
    # TODO: Implementar cuando se tenga control de despacho de órdenes
    pass


def actualizar_inventario_material(materia_prima, almacen):
    """
    Actualiza el registro de InventarioMaterial basándose en el Kardex.

    Este método sincroniza la tabla de inventario con los saldos del Kardex.
    """
    from innoquim.apps.inventario.models import Kardex
    from innoquim.apps.inventario_material.models import InventarioMaterial

    # Obtener saldo actual del Kardex
    saldo = Kardex.obtener_saldo_actual(almacen, materia_prima)

    # Buscar o crear registro en InventarioMaterial
    inventario, created = InventarioMaterial.objects.get_or_create(
        materia_prima_id=materia_prima,
        almacen_id=almacen,
        defaults={"unidad_id": materia_prima.unidad_id, "cantidad": saldo["cantidad"]},
    )

    # Si ya existe, actualizar cantidad
    if not created:
        inventario.cantidad = saldo["cantidad"]
        inventario.save()
