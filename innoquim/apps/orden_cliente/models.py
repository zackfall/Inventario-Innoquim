from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum


class OrdenCliente(models.Model):
    """
    Modelo para gestionar ordenes de clientes de INNO-QUIM.
    Registra pedidos de clientes con items, calculos de impuestos y totales.
    
    Relaciones:
    - client: FK a tabla cliente (quien realiza la orden)
    - items: Relacion inversa con OrdenItem (productos de la orden)
    
    Notas:
    - tax_amount y total_amount se calculan automaticamente via update_totals()
    - El metodo save() recalcula totales si cambia tax_rate
    - Los items se gestionan mediante el modelo OrdenItem relacionado
    """
    
    # =================================================================
    # CHOICES Y CONSTANTES
    # =================================================================
    
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("confirmed", "Confirmada"),
        ("in_progress", "En Proceso"),
        ("completed", "Completada"),
        ("cancelled", "Cancelada"),
    )

    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================
    
    # client: FK a tabla cliente
    # on_delete=PROTECT: no permite borrar cliente si tiene ordenes asociadas
    # related_name="ordenes": acceso inverso desde Cliente.ordenes.all()
    client = models.ForeignKey(
        "cliente.Cliente",
        on_delete=models.PROTECT,
        related_name="ordenes",
        verbose_name="Cliente",
        help_text="Cliente que realiza la orden"
    )
    
    # order_code: Codigo unico de la orden
    # unique=True: evita duplicados de codigos
    order_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Codigo de Orden",
        help_text="Codigo unico de identificacion de la orden"
    )
    
    order_date = models.DateField(
        verbose_name="Fecha de Orden",
        help_text="Fecha en que se realiza la orden"
    )
    
    # status: Estado actual de la orden
    # default="pending": nuevas ordenes inician como pendientes
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Estado",
        help_text="Estado actual de la orden"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
        help_text="Observaciones o instrucciones especiales"
    )

    # =================================================================
    # CAMPOS DE IMPUESTOS Y TOTALES (SNAPSHOT)
    # =================================================================
    
    # tax_rate: Porcentaje de impuesto aplicado a esta orden
    # Se guarda como snapshot en el momento de la orden
    # Formato: 15.00 representa 15%
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Tasa de Impuesto (%)",
        help_text="Porcentaje de impuesto aplicado (ej: 15.00 para 15%)"
    )
    
    # tax_amount: Monto calculado de impuestos
    # Se calcula automaticamente en update_totals()
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Monto de Impuesto",
        help_text="Monto calculado de impuestos (autocalculado)"
    )
    
    # total_amount: Total final de la orden (subtotales + impuestos)
    # Se calcula automaticamente en update_totals()
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total de Orden",
        help_text="Monto total de la orden (autocalculado)"
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
        db_table = "orden_cliente"
        verbose_name = "Orden de Cliente"
        verbose_name_plural = "Órdenes de Cliente"
        ordering = ["-order_date"]  # Ordenes mas recientes primero

    def __str__(self):
        """Representacion legible del objeto (usado en admin y logs)"""
        return f"{self.order_code} - {self.client}"

    def update_totals(self):
        """
        Calcula y actualiza los totales de la orden.
        
        Logica:
        1. Suma todos los subtotales de los items relacionados
        2. Calcula el impuesto aplicando tax_rate al total de items
        3. Calcula el total final (items + impuesto)
        4. Actualiza la BD usando queryset.update() para evitar recursion
        5. Actualiza la instancia en memoria para mantener consistencia
        
        IMPORTANTE: Usa queryset.update() en lugar de self.save() para
        evitar bucles infinitos con el metodo save() sobreescrito
        """
        # Sumar subtotales de todos los items relacionados
        items_total = self.items.aggregate(total=Sum("subtotal"))["total"] or Decimal("0.00")
        
        # Calcular impuesto: items_total * (tax_rate / 100)
        # Ejemplo: 100.00 * (15.00 / 100) = 15.00
        tax = (items_total * (self.tax_rate or Decimal("0.00"))) / Decimal("100.00")
        tax_amt = tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calcular total final: items + impuesto
        total_amt = (items_total + tax_amt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Actualizar BD sin self.save() para evitar bucles
        self.__class__.objects.filter(pk=self.pk).update(
            tax_amount=tax_amt,
            total_amount=total_amt
        )

        # Mantener la instancia en memoria consistente
        self.tax_amount = tax_amt
        self.total_amount = total_amt

    def save(self, *args, **kwargs):
        """
        Override del metodo save() para recalcular totales cuando cambia tax_rate.
        
        Logica:
        1. Si la orden ya existe, obtiene el tax_rate anterior de la BD
        2. Guarda el registro con super().save()
        3. Si es nueva orden O si cambio tax_rate, recalcula totales
        
        NOTA: update_totals() usa queryset.update() internamente,
        por eso es seguro llamarlo aqui sin crear bucles infinitos
        """
        old_rate = None
        if self.pk:
            # Obtener tax_rate anterior si la orden ya existe
            old_rate = self.__class__.objects.filter(pk=self.pk).values_list("tax_rate", flat=True).first()
        
        # Guardar el registro normalmente
        super().save(*args, **kwargs)
        
        # Recalcular totales si es nueva O si cambio tax_rate
        if old_rate is None or old_rate != self.tax_rate:
            self.update_totals()