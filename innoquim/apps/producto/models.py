from django.db import models


class Producto(models.Model):
    product_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    categoria_id = models.ForeignKey(
        "categoria.Categoria",
        on_delete=models.PROTECT,
        related_name="productos",
        limit_choices_to={'tipo': 'PRODUCT'},
        verbose_name="Categoría",
        help_text="Categoría del producto terminado"
    )
    unit = models.ForeignKey(
        "unidad.Unidad", on_delete=models.PROTECT, related_name="productos"
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Precio de costo (último precio de compra o costo calculado)
    costo_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=0.0000,
        verbose_name="Costo Unitario",
        help_text="Último costo unitario de producción o compra"
    )
    stock = models.PositiveIntegerField(default=0)
    
    # Control de niveles de stock para productos terminados
    stock_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima requerida en inventario para alertas de reabastecimiento"
    )
    
    stock_maximo = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Stock Máximo",
        help_text="Cantidad máxima permitida en inventario (opcional, para control de sobreinventario)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_code} - {self.name}"
    
    @property
    def stock_status(self):
        """Retorna el estado del stock basado en los niveles mínimo y máximo"""
        if self.stock <= self.stock_minimo:
            return "BAJO"
        elif self.stock_maximo and self.stock >= self.stock_maximo:
            return "ALTO"
        else:
            return "NORMAL"
    
    @property
    def necesita_reabastecimiento(self):
        """Retorna True si el stock está por debajo del mínimo"""
        return self.stock <= self.stock_minimo
    
    @property
    def sobre_inventario(self):
        """Retorna True si el stock está por encima del máximo"""
        return self.stock_maximo and self.stock >= self.stock_maximo