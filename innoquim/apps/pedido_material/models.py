from django.db import models
from innoquim.apps.usuario.models import Usuario
from innoquim.apps.proveedor.models import Proveedor


class PedidoMaterial(models.Model):
    """
    Modelo para registrar pedidos de materias primas a proveedores.

    Proposito:
    - Llevar un registro historico de pedidos realizados
    - Saber quien hizo cada pedido (trazabilidad)
    - No tiene flujo de aprobacion (solo registro)

    Relaciones:
    - proveedor_id: A QUIEN se le hizo el pedido
    - usuario_registro: QUIEN registro el pedido en el sistema

    Notas:
    - Un pedido puede tener varios items (tabla pedido_item)
    - Es opcional registrar pedidos (no afecta el inventario directamente)
    - Los items del pedido se registran en pedido_item
    """

    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================

    # pedido_material_id: PRIMARY KEY autogenerada
    # Formato: PM + 6 digitos (ej: PM000001, PM000002, ...)
    pedido_material_id = models.CharField(
        max_length=8,
        primary_key=True,
        editable=False,
        verbose_name="ID Pedido Material",
        help_text="Codigo unico autogenerado (formato: PM000001)",
    )

    # =================================================================
    # RELACIONES (FOREIGN KEYS)
    # =================================================================

    # proveedor_id: A QUIEN se le hizo el pedido
    # on_delete=PROTECT: no permite borrar proveedor si tiene pedidos registrados
    proveedor_id = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        verbose_name="Proveedor",
        help_text="Proveedor al que se le solicito el material",
    )

    # usuario_registro: QUIEN registro el pedido en el sistema
    # on_delete=PROTECT: no permite borrar usuario si tiene pedidos
    # related_name: permite acceder a los pedidos desde el usuario
    # Ejemplo: usuario.pedidos_materiales.all()
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="pedidos_materiales",
        verbose_name="Usuario que Registro",
        help_text="Empleado que registro el pedido en el sistema",
    )

    # =================================================================
    # FECHAS DEL PEDIDO
    # =================================================================

    fecha_pedido = models.DateField(
        verbose_name="Fecha del Pedido",
        help_text="Fecha en que se realizo el pedido al proveedor",
    )

    # fecha_entrega_esperada: cuando deberia llegar (opcional)
    fecha_entrega_esperada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Entrega Esperada",
        help_text="Fecha estimada de llegada del pedido",
    )

    # =================================================================
    # INFORMACION ADICIONAL
    # =================================================================

    # numero_orden_compra: numero de OC del sistema contable (opcional)
    numero_orden_compra = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Numero de Orden de Compra",
        help_text="Numero de OC externo o del sistema contable",
    )

    # observaciones: notas sobre el pedido
    observaciones = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observaciones",
        help_text="Notas o comentarios sobre el pedido",
    )

    # =================================================================
    # CAMPOS DE AUDITORIA (automaticos)
    # =================================================================

    # auto_now_add=True: se llena SOLO al crear el registro
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creacion"
    )

    # auto_now=True: se actualiza CADA VEZ que se modifica
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Ultima Actualizacion"
    )

    class Meta:
        db_table = "pedido_material"
        verbose_name = "Pedido de Material"
        verbose_name_plural = "Pedidos de Materiales"
        ordering = ["-fecha_pedido", "-pedido_material_id"]  # Mas recientes primero

        # Indices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=["proveedor_id"]),
            models.Index(fields=["fecha_pedido"]),
            models.Index(fields=["usuario_registro"]),
        ]

    def __str__(self):
        """Representacion legible del objeto"""
        return f"{self.pedido_material_id} - {self.proveedor_id.nombre_empresa} ({self.fecha_pedido})"

    def save(self, *args, **kwargs):
        """
        Override del metodo save() para autogenerar pedido_material_id.
        Formato: PM + 6 digitos (PM000001, PM000002, ...)
        """
        if not self.pedido_material_id:
            last_pedido = PedidoMaterial.objects.order_by("-pedido_material_id").first()

            if last_pedido and last_pedido.pedido_material_id:
                last_number = int(last_pedido.pedido_material_id[2:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.pedido_material_id = f"PM{new_number:06d}"

        super().save(*args, **kwargs)
