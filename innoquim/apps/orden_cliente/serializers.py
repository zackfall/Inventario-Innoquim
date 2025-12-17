from rest_framework import serializers
from .models import OrdenCliente
from innoquim.apps.orden_item.serializers import OrdenItemSerializer
from innoquim.apps.orden_item.models import OrdenItem


class OrdenClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo OrdenCliente.
    Convierte objetos Python <-> JSON para la API REST.
    Gestiona creacion/actualizacion de ordenes con sus items anidados.
    """
    
    # Campo adicional de solo lectura para mostrar el nombre del cliente
    # Evita hacer una peticion extra para obtener el nombre de la empresa
    client_name = serializers.CharField(
        source="client.nombre_empresa",
        read_only=True
    )
    
    # Items anidados: permite crear/actualizar items dentro de la orden
    # many=True: acepta una lista de items
    # required=False: permite crear orden sin items inicialmente
    items = OrdenItemSerializer(many=True, required=False)
    
    # Campo calculado para mostrar el total
    # Usa get_total() para obtener el valor
    total = serializers.SerializerMethodField()

    # Campos de impuestos y totales
    # tax_rate es editable, los demas son calculados
    tax_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False
    )
    tax_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrdenCliente
        fields = [
            "id",
            "client",
            "client_name",  # Campo extra para lectura
            "order_code",
            "order_date",
            "status",
            "notes",
            "tax_rate",
            "tax_amount",      # Calculado automaticamente
            "total_amount",    # Calculado automaticamente
            "total",           # Alias de total_amount
            "items",           # Items anidados
            "created_at",
            "updated_at",
        ]
        # Campos que NO se pueden modificar via API
        read_only_fields = ["created_at", "updated_at", "tax_amount", "total_amount"]

    def get_total(self, obj):
        """Retorna el total_amount de la orden"""
        return obj.total_amount

    def create(self, validated_data):
        """
        Crea una nueva orden con sus items.
        
        Logica:
        1. Extrae los items del validated_data
        2. Crea la orden sin items
        3. Crea cada item asociado a la orden (cada OrdenItem calcula su subtotal)
        4. Recalcula totales de la orden (suma subtotales + aplica impuestos)
        """
        items_data = validated_data.pop("items", [])
        order = super().create(validated_data)
        
        # Crear items asociados (cada OrdenItem calculara subtotal en su save)
        for item in items_data:
            OrdenItem.objects.create(order=order, **item)
        
        # Recalcular totales de la orden
        order.update_totals()
        return order

    def update(self, instance, validated_data):
        """
        Actualiza una orden existente y sus items.
        
        Estrategia simple: si se envian items, borra los existentes y recrea
        Logica:
        1. Extrae los items del validated_data
        2. Actualiza la orden (campos principales)
        3. Si se enviaron items: borra items existentes y crea los nuevos
        4. Recalcula totales de la orden
        """
        items_data = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        
        if items_data is not None:
            # Estrategia simple: borrar existentes y recrear
            instance.items.all().delete()
            for item in items_data:
                OrdenItem.objects.create(order=instance, **item)
        
        # Recalcular totales de la orden
        instance.update_totals()
        return instance