from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


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
    stock = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock",
        help_text="Cantidad actual en inventario"
    )
    
    # Control de niveles de stock para productos terminados
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima requerida en inventario para alertas de reabastecimiento"
    )
    
    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
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
    
    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.stock_maximo is not None and self.stock_minimo > self.stock_maximo:
            raise ValidationError({
                'stock_minimo': 'El stock mínimo no puede ser mayor que el stock máximo.'
    })
    
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