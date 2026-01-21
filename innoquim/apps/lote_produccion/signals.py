"""
Signals para actualizar stock automáticamente al completar/cancelar lotes
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import LoteProduccion
from innoquim.apps.producto.models import Producto
from innoquim.apps.materia_prima.models import MateriaPrima
from innoquim.apps.inventario.models import Kardex


@receiver(post_save, sender=LoteProduccion)
def actualizar_stocks_al_cambiar_estado(sender, instance, created, **kwargs):
    """
    Al cambiar el estado de un lote a COMPLETADO:
    - Aumenta el stock del PRODUCTO en produced_quantity
    - Disminuye el stock de cada MATERIA PRIMA en used_quantity
    - Crea registros en el Kardex
    
    Al cambiar a CANCELADO:
    - No hace nada (el lote queda como registro para auditoría)
    """
    
    # Solo procesar si el lote fue actualizado (no creado)
    if created:
        return
    
    # Si el estado es COMPLETADO
    if instance.status == "completed":
        try:
            from django.contrib.contenttypes.models import ContentType
            from innoquim.apps.almacen.models import Almacen
            
            # 1. Actualizar stock del PRODUCTO (sumar)
            producto = instance.product
            producto.stock += int(instance.produced_quantity)
            producto.save()
            
            # 2. Obtener el almacén (primera opción o predeterminado)
            almacen = Almacen.objects.first()
            if not almacen:
                print(f"No hay almacén disponible para registrar movimientos del lote {instance.batch_code}")
                return
            
            # 3. Actualizar stock de cada MATERIA PRIMA (restar) y crear Kardex
            for material in instance.materiales.all():
                materia_prima = material.raw_material
                materia_prima.stock_actual -= material.used_quantity
                materia_prima.save()
                
                # Crear registro en Kardex (salida de materia prima)
                try:
                    Kardex.objects.create(
                        almacen=almacen,
                        content_type=ContentType.objects.get_for_model(MateriaPrima),
                        object_id=str(materia_prima.id),
                        tipo_movimiento="SALIDA",
                        motivo="PRODUCCION",
                        cantidad=material.used_quantity,
                        costo_unitario=materia_prima.precio_unitario or 0,
                        costo_total=(material.used_quantity * (materia_prima.precio_unitario or 0)),
                        saldo_cantidad=materia_prima.stock_actual,
                        saldo_costo_total=0,
                        saldo_costo_promedio=0,
                        referencia_id=str(instance.id),
                        observaciones=f"Material usado en lote {instance.batch_code}",
                    )
                except Exception as kardex_error:
                    print(f"Error al crear registro Kardex: {str(kardex_error)}")
            
        except Exception as e:
            print(f"Error al actualizar stocks del lote {instance.batch_code}: {str(e)}")
