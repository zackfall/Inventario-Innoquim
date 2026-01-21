from rest_framework import serializers
from .models import RecepcionMaterial
from innoquim.apps.almacen.serializers import AlmacenSerializer
from innoquim.apps.materia_prima.serializers import MateriaPrimaSerializer

class RecepcionMaterialSerializer(serializers.ModelSerializer):
    almacen_detail = AlmacenSerializer(source='almacen', read_only=True)
    materia_prima_detail = MateriaPrimaSerializer(source='materia_prima', read_only=True)
    
    # Campo calculado para mostrar el total formateado
    total_formateado = serializers.SerializerMethodField()

    class Meta:
        model = RecepcionMaterial
        fields = [
            'id', 
            'materia_prima', 
            'materia_prima_detail',
            'cantidad', 
            'costo_unitario', 
            'total',
            'total_formateado',
            'proveedor', 
            'almacen', 
            'almacen_detail',
            'fecha_de_recepcion', 
            'numero_de_factura', 
            'observaciones',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'total']
    
    def get_total_formateado(self, obj):
        """Formatear el total como moneda"""
        if obj.total:
            return f"${obj.total:,.2f}"
        return "$0.00"
    
    def validate(self, data):
        """Validar que los campos necesarios estén completos para el cálculo"""
        cantidad = data.get('cantidad')
        costo_unitario = data.get('costo_unitario')
        
        if cantidad and costo_unitario:
            data['total'] = cantidad * costo_unitario
        
        return data