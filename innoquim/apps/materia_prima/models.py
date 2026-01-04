from django.db import models

from innoquim.apps.categoria.models import Categoria
from innoquim.apps.unidad.models import Unidad


class MateriaPrima(models.Model):
    """
    Modelo para gestionar materias primas de INNO-QUIM.
    Ingredientes y componentes usados en la produccion de productos quimicos.

    Relaciones:
    - unidad_id: FK a tabla unidad (como se mide: kg, litros, etc)

    Notas:
    - materia_prima_id se autogenera con formato MP000001 (ver metodo save())
    - codigo debe ser unico para evitar duplicados
    - densidad y stock_maximo son opcionales
    """

    # =================================================================
    # CAMPOS PRINCIPALES
    # =================================================================

    # materia_prima_id: PRIMARY KEY autogenerada
    # Formato: MP + 6 digitos (ej: MP000001, MP000002, ...)
    # Se genera automaticamente en save() basandose en el ultimo registro
    materia_prima_id = models.CharField(
        max_length=8,  # MP (2) + 6 digitos = 8 caracteres max
        primary_key=True,
        editable=False,  # No permitir edicion manual
        verbose_name="ID Materia Prima",
        help_text="Codigo unico autogenerado (formato: MP000001)",
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
        help_text="Nombre de la materia prima (ej: Acido Sulfurico)",
    )

    # codigo: Codigo interno/SKU para identificacion rapida
    # unique=True: evita duplicados de codigos
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Codigo",
        help_text="Codigo interno/SKU de la materia prima (ej: AC-SUL-98)",
    )

    # descripcion: campo opcional para especificaciones tecnicas
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripcion",
        help_text="Descripcion detallada, especificaciones tecnicas, pureza, etc",
    )

    categoria_id = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='materias_primas',
        limit_choices_to={'tipo': 'RAW_MATERIAL'},
        verbose_name="Categoria",
        help_text="Categoria de clasificacion de la materia prima",
    )
    
    # =================================================================
    # RELACIONES (FOREIGN KEYS)
    # =================================================================

    # unidad_id: FK a tabla unidad
    # on_delete=PROTECT: no permite borrar unidad si tiene materias primas asociadas
    # Razon: protege la integridad de datos (evita quedarse sin unidad de referencia)
    unidad_id = models.ForeignKey(
        Unidad,
        on_delete=models.PROTECT,
        verbose_name="Unidad de Medida",
        help_text="Unidad en que se mide (kg, litros, etc)",
    )

    # =================================================================
    # PROPIEDADES FISICAS Y STOCK
    # =================================================================

    # densidad: propiedad fisica opcional
    # max_digits=10, decimal_places=4: permite valores como 1.8400 o 1234.5678
    densidad = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name="Densidad",
        help_text="Densidad de la materia prima en g/cm3 o kg/L (opcional)",
    )

    # stock_minimo: alerta cuando se debe pedir mas
    # default=0: si no se especifica, asume 0
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Stock Minimo",
        help_text="Cantidad minima requerida en inventario",
    )

    # stock_maximo: limite superior opcional
    stock_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Stock Maximo",
        help_text="Cantidad maxima permitida en inventario (opcional)",
    )

    # costo promedio para que Kardex sepa el valor actual del producto
    costo_promedio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=0.0000,
        verbose_name="Costo Promedio ($)",
        help_text="Costo promedio unitario actualizado por el Kardex",
    )

    # =================================================================
    # CAMPOS DE AUDITORIA (automaticos)
    # =================================================================

    # auto_now_add=True: se llena SOLO al crear el registro
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creacion"
    )

    # auto_now=True: se actualiza CADA VEZ que se modifica el registro
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Ultima Actualizacion"
    )

    class Meta:
        db_table = "materia_prima"  # Nombre de la tabla en PostgreSQL
        verbose_name = "Materia Prima"
        verbose_name_plural = "Materias Primas"
        ordering = ["materia_prima_id"]  # Orden por defecto en consultas

        # Indices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=["codigo"]),  # Busquedas por codigo
            models.Index(fields=["nombre"]),  # Busquedas por nombre
        ]

    def __str__(self):
        """Representacion legible del objeto (usado en admin y logs)"""
        return f"{self.materia_prima_id} - {self.nombre}"

    def save(self, *args, **kwargs):
        """
        Override del metodo save() para autogenerar materia_prima_id.

        Logica:
        1. Si es un registro nuevo (no tiene materia_prima_id)
        2. Busca el ultimo materia_prima_id en la BD
        3. Extrae el numero, suma 1
        4. Formatea con padding de 6 digitos

        Formato: MP + 6 digitos (MP000001, MP000002, ...)
        Soporta hasta 999,999 materias primas
        """
        if not self.materia_prima_id:
            # Obtener la ultima materia prima ordenada descendente
            last_material = MateriaPrima.objects.order_by("-materia_prima_id").first()

            if last_material and last_material.materia_prima_id:
                # Extraer numero del formato MP000001 -> 1
                # [2:] elimina los primeros 2 caracteres "MP"
                last_number = int(last_material.materia_prima_id[2:])
                new_number = last_number + 1
            else:
                # Primera insercion en la tabla
                new_number = 1

            # f-string con formato :06d = padding de 6 digitos con ceros
            self.materia_prima_id = f"MP{new_number:06d}"

        # Llamar al save() original de Django
        super().save(*args, **kwargs)

