from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


class Kardex(models.Model):
    """
    Sistema de control de inventario mediante Kardex.
    Registra TODOS los movimientos de entrada y salida de materias primas y productos.

    Características:
    - Usa Generic Foreign Key para manejar MateriaPrima Y Producto
    - Calcula costo promedio ponderado automáticamente
    - Mantiene saldos actualizados después de cada movimiento
    - Inmutable: una vez creado un registro, NO se modifica (solo se consulta)
    """

    TIPO_OPERACION = (
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    )

    ORIGEN_CHOICES = (
        ("COMPRA", "Compra/Recepción"),
        ("PRODUCCION", "Producción"),
        ("VENTA", "Venta/Orden Cliente"),
        ("AJUSTE", "Ajuste de Inventario"),
        ("DEVOLUCION", "Devolución"),
    )

    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Movimiento")
    almacen = models.ForeignKey(
        "almacen.Almacen", on_delete=models.PROTECT, verbose_name="Almacén"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        limit_choices_to={"model__in": ("materiaprima", "producto")},
    )
    object_id = models.CharField(max_length=8)  # MP000001 o ID de producto
    item = GenericForeignKey("content_type", "object_id")

    tipo_movimiento = models.CharField(
        max_length=10, choices=TIPO_OPERACION, verbose_name="Tipo de Movimiento"
    )
    motivo = models.CharField(
        max_length=20, choices=ORIGEN_CHOICES, verbose_name="Motivo del Movimiento"
    )
    cantidad = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Cantidad del Movimiento"
    )

    costo_unitario = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name="Costo Unitario"
    )
    costo_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Costo Total del Movimiento",
        help_text="cantidad * costo_unitario",
    )

    saldo_cantidad = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Saldo en Cantidad"
    )
    saldo_costo_total = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Saldo en Valor Monetario"
    )
    saldo_costo_promedio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name="Costo Promedio después del Movimiento",
        help_text="saldo_costo_total / saldo_cantidad",
    )

    referencia_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="ID de Referencia",
        help_text="ID de recepción, orden, lote, etc.",
    )
    observaciones = models.TextField(
        null=True, blank=True, verbose_name="Observaciones"
    )
    usuario = models.ForeignKey(
        "usuario.Usuario",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Usuario que registró el movimiento",
    )

    class Meta:
        verbose_name = "Kardex"
        verbose_name_plural = "Kardex"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["almacen"]),
            models.Index(fields=["fecha"]),
            models.Index(fields=["tipo_movimiento"]),
        ]

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.item} - {self.cantidad} ({self.fecha})"

    def save(self, *args, **kwargs):
        """
        Calcula costo_total antes de guardar.
        IMPORTANTE: Los saldos deben calcularse ANTES de llamar a save()
        usando el método estático registrar_movimiento()
        """
        if not self.costo_total:
            self.costo_total = (self.cantidad * self.costo_unitario).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        super().save(*args, **kwargs)

    @staticmethod
    def registrar_movimiento(
        almacen,
        item,
        tipo_movimiento,
        motivo,
        cantidad,
        costo_unitario,
        referencia_id=None,
        observaciones=None,
        usuario=None,
    ):
        """
        Método estático para registrar movimientos en el Kardex.

        Este método:
        1. Obtiene el último saldo del item en el almacén
        2. Calcula los nuevos saldos según el tipo de movimiento
        3. Actualiza el costo promedio en caso de entrada
        4. Crea el registro de Kardex
        5. Actualiza el costo_promedio en MateriaPrima si aplica

        Parámetros:
            almacen: Objeto Almacen
            item: Objeto MateriaPrima o Producto
            tipo_movimiento: "ENTRADA" o "SALIDA"
            motivo: Razón del movimiento
            cantidad: Cantidad a mover
            costo_unitario: Costo unitario del movimiento
            referencia_id: ID de referencia (opcional)
            observaciones: Notas adicionales (opcional)
            usuario: Usuario que registra (opcional)

        Retorna:
            Objeto Kardex creado

        Ejemplo de uso:
            from innoquim.apps.inventario.models import Kardex

            kardex = Kardex.registrar_movimiento(
                almacen=almacen_obj,
                item=materia_prima_obj,
                tipo_movimiento="ENTRADA",
                motivo="COMPRA",
                cantidad=100,
                costo_unitario=Decimal("5.50"),
                referencia_id="RM000001",
                usuario=request.user
            )
        """
        from django.contrib.contenttypes.models import ContentType

        cantidad = Decimal(str(cantidad))
        costo_unitario = Decimal(str(costo_unitario))

        # Obtener el content_type del item
        content_type = ContentType.objects.get_for_model(item)

        # Buscar el último registro de Kardex para este item en este almacén
        ultimo_kardex = (
            Kardex.objects.filter(
                content_type=content_type, object_id=item.pk, almacen=almacen
            )
            .order_by("-fecha", "-id")
            .first()
        )

        # Saldos anteriores (si no hay registro previo, son 0)
        if ultimo_kardex:
            saldo_cantidad_anterior = ultimo_kardex.saldo_cantidad
            saldo_costo_total_anterior = ultimo_kardex.saldo_costo_total
        else:
            saldo_cantidad_anterior = Decimal("0.00")
            saldo_costo_total_anterior = Decimal("0.00")

        # Calcular nuevos saldos según el tipo de movimiento
        if tipo_movimiento == "ENTRADA":
            # ENTRADA: Suma cantidad y costo
            nuevo_saldo_cantidad = saldo_cantidad_anterior + cantidad
            costo_movimiento = cantidad * costo_unitario
            nuevo_saldo_costo_total = saldo_costo_total_anterior + costo_movimiento

            # Calcular nuevo costo promedio ponderado
            if nuevo_saldo_cantidad > 0:
                nuevo_costo_promedio = (
                    nuevo_saldo_costo_total / nuevo_saldo_cantidad
                ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            else:
                nuevo_costo_promedio = Decimal("0.0000")

        elif tipo_movimiento == "SALIDA":
            # SALIDA: Resta cantidad al costo promedio actual
            nuevo_saldo_cantidad = saldo_cantidad_anterior - cantidad

            # Obtener el costo promedio actual
            if ultimo_kardex and ultimo_kardex.saldo_cantidad > 0:
                costo_promedio_actual = ultimo_kardex.saldo_costo_promedio
            else:
                costo_promedio_actual = costo_unitario

            # La salida se valora al costo promedio actual
            costo_movimiento = cantidad * costo_promedio_actual
            nuevo_saldo_costo_total = saldo_costo_total_anterior - costo_movimiento

            # El costo promedio se mantiene igual en salidas
            nuevo_costo_promedio = costo_promedio_actual

            # Ajuste: si el saldo queda negativo, establecer en 0
            if nuevo_saldo_cantidad < 0:
                nuevo_saldo_cantidad = Decimal("0.00")
                nuevo_saldo_costo_total = Decimal("0.00")
                nuevo_costo_promedio = Decimal("0.0000")
        else:
            raise ValueError(f"Tipo de movimiento inválido: {tipo_movimiento}")

        # Crear el registro de Kardex
        kardex = Kardex.objects.create(
            almacen=almacen,
            content_type=content_type,
            object_id=item.pk,
            tipo_movimiento=tipo_movimiento,
            motivo=motivo,
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            saldo_cantidad=nuevo_saldo_cantidad,
            saldo_costo_total=nuevo_saldo_costo_total,
            saldo_costo_promedio=nuevo_costo_promedio,
            referencia_id=referencia_id,
            observaciones=observaciones,
            usuario=usuario,
        )

        # Actualizar el costo_promedio en MateriaPrima si aplica
        if content_type.model == "materiaprima":
            from innoquim.apps.materia_prima.models import MateriaPrima

            MateriaPrima.objects.filter(pk=item.pk).update(
                costo_promedio=nuevo_costo_promedio
            )

        return kardex

    @staticmethod
    def obtener_saldo_actual(almacen, item):
        """
        Obtiene el saldo actual de un item en un almacén.

        Retorna:
            dict con 'cantidad', 'costo_total', 'costo_promedio'
            Si no hay movimientos, retorna valores en 0
        """
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(item)

        ultimo_kardex = (
            Kardex.objects.filter(
                content_type=content_type, object_id=item.pk, almacen=almacen
            )
            .order_by("-fecha", "-id")
            .first()
        )

        if ultimo_kardex:
            return {
                "cantidad": ultimo_kardex.saldo_cantidad,
                "costo_total": ultimo_kardex.saldo_costo_total,
                "costo_promedio": ultimo_kardex.saldo_costo_promedio,
            }
        else:
            return {
                "cantidad": Decimal("0.00"),
                "costo_total": Decimal("0.00"),
                "costo_promedio": Decimal("0.0000"),
            }


class AjusteInventario(models.Model):
    """
    Modelo para registrar ajustes manuales de inventario.
    Usado cuando hay diferencias físicas vs sistema, mermas, etc.
    """

    TIPO_AJUSTE = (
        ("POSITIVO", "Ajuste Positivo (+ añadir)"),
        ("NEGATIVO", "Ajuste Negativo (- quitar)"),
    )

    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha del Ajuste")
    almacen = models.ForeignKey("almacen.Almacen", on_delete=models.PROTECT, verbose_name="Almacén")

    # Item a ajustar (MateriaPrima o Producto)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
                                   limit_choices_to={"model__in": ("materiaprima", "producto")})
    object_id = models.CharField(max_length=8)
    item = GenericForeignKey("content_type", "object_id")

    tipo_ajuste = models.CharField(max_length=10, choices=TIPO_AJUSTE, verbose_name="Tipo de Ajuste")
    cantidad = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Cantidad Ajustada")
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Costo Unitario")

    motivo = models.TextField(verbose_name="Motivo del Ajuste", help_text="Explicación del ajuste")
    responsable = models.ForeignKey("usuario.Usuario", on_delete=models.PROTECT, verbose_name="Responsable")

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ajuste de Inventario"
        verbose_name_plural = "Ajustes de Inventario"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Ajuste {self.tipo_ajuste} - {self.item} - {self.cantidad}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Registrar en Kardex
        tipo_movimiento = "ENTRADA" if self.tipo_ajuste == "POSITIVO" else "SALIDA"
        motivo = "AJUSTE"

        Kardex.registrar_movimiento(
            almacen=self.almacen,
            item=self.item,
            tipo_movimiento=tipo_movimiento,
            motivo=motivo,
            cantidad=self.cantidad,
            costo_unitario=self.costo_unitario,
            referencia_id=f"AJUSTE{self.id}",
            observaciones=f"Ajuste manual: {self.motivo}",
            usuario=self.responsable,
        )


class Devolucion(models.Model):
    """
    Modelo para registrar devoluciones de productos vendidos.
    """

    fecha = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Devolución")
    almacen = models.ForeignKey("almacen.Almacen", on_delete=models.PROTECT, verbose_name="Almacén")

    # Orden original (opcional, para trazabilidad)
    orden_original = models.ForeignKey(
        "orden_cliente.OrdenCliente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Orden Original"
    )

    # Producto devuelto
    producto = models.ForeignKey("producto.Producto", on_delete=models.PROTECT, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad Devuelta")

    # Información financiera
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Devolución")

    motivo = models.TextField(verbose_name="Motivo de Devolución")
    cliente = models.ForeignKey("cliente.Cliente", on_delete=models.PROTECT, verbose_name="Cliente")

    # Estado de la devolución
    ESTADO_CHOICES = (
        ("PENDIENTE", "Pendiente de Procesamiento"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
        ("PROCESADA", "Procesada"),
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default="PENDIENTE")

    responsable = models.ForeignKey("usuario.Usuario", on_delete=models.PROTECT, verbose_name="Responsable")

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Devolución"
        verbose_name_plural = "Devoluciones"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Devolución {self.producto.name} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        # Calcular total si no está establecido
        if not self.total and self.cantidad and self.precio_unitario:
            self.total = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)

        # Solo registrar en Kardex si está procesada
        if self.estado == "PROCESADA":
            Kardex.registrar_movimiento(
                almacen=self.almacen,
                item=self.producto,
                tipo_movimiento="ENTRADA",
                motivo="DEVOLUCION",
                cantidad=Decimal(str(self.cantidad)),
                costo_unitario=self.precio_unitario,
                referencia_id=f"DEV{self.id}",
                observaciones=f"Devolución de orden {self.orden_original.order_code if self.orden_original else 'N/A'}: {self.motivo}",
                usuario=self.responsable,
            )
