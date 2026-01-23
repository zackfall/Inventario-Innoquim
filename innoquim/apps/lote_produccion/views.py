from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import LoteProduccion
from .serializers import (
    LoteProduccionSerializer,
    LoteProduccionCreateSerializer
)
from innoquim.apps.material_produccion.models import MaterialProduccion
from innoquim.apps.material_produccion.serializers import MaterialProduccionSerializer


class LoteProduccionViewSet(viewsets.ModelViewSet):
    
    queryset = LoteProduccion.objects.all().select_related(
        'product', 'unit', 'almacen', 'production_manager'
    ).prefetch_related('materiales').order_by("-production_date")
    
    filterset_fields = ["product", "status", "production_manager", "almacen"]
    search_fields = ["batch_code", "product__name"]
    
    def get_serializer_class(self):
        """Usar serializer diferente para create"""
        if self.action == 'create':
            return LoteProduccionCreateSerializer
        return LoteProduccionSerializer
    @action(detail=True, methods=["get"], url_path="materiales")
    def list_materiales(self, request, pk=None):
        lote = self.get_object()
        materiales = MaterialProduccion.objects.filter(batch=lote).select_related(
            'raw_material', 'unit'
        )
        serializer = MaterialProduccionSerializer(materiales, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="materiales")
    def add_material(self, request, pk=None):
        lote = self.get_object()
        
        # No permitir agregar materiales a lotes completados
        if lote.status == 'completed':
            return Response(
                {"error": "No se pueden agregar materiales a un lote completado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MaterialProduccionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(batch=lote)
            
            # Recalcular costos del lote
            lote.calcular_costo_materiales()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, 
        methods=["get", "put", "delete"], 
        url_path=r"materiales/(?P<material_id>\d+)"
    )
    def manage_material(self, request, pk=None, material_id=None):
        """
        Gestionar un material específico del lote.
        
        - GET: Ver detalle del material
        - PUT: Actualizar cantidad del material
        - DELETE: Eliminar material del lote
        """
        lote = self.get_object()
        material = get_object_or_404(
            MaterialProduccion,
            id=material_id,
            batch=lote
        )
        
        # No permitir modificar materiales de lotes completados
        if lote.status == 'completed' and request.method in ['PUT', 'DELETE']:
            return Response(
                {"error": "No se pueden modificar materiales de un lote completado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == "GET":
            serializer = MaterialProduccionSerializer(material)
            return Response(serializer.data)
        
        elif request.method == "PUT":
            serializer = MaterialProduccionSerializer(
                material,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                
                # Recalcular costos del lote
                lote.calcular_costo_materiales()
                
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == "DELETE":
            material.delete()
            
            # Recalcular costos del lote
            lote.calcular_costo_materiales()
            
            return Response(
                {"message": "Material eliminado exitosamente"},
                status=status.HTTP_204_NO_CONTENT
            )
    
    
    @action(detail=True, methods=['post'], url_path='completar')
    @transaction.atomic
    def completar(self, request, pk=None):
        lote = self.get_object()
        
        try:
            lote.completar_produccion(usuario=request.user)
            
            serializer = self.get_serializer(lote)
            return Response({
                "message": "Lote completado exitosamente",
                "lote": serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al completar lote: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        lote = self.get_object()
        
        if lote.status == 'completed':
            return Response(
                {"error": "No se puede cancelar un lote completado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if lote.status == 'cancelled':
            return Response(
                {"error": "Este lote ya está cancelado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lote.status = 'cancelled'
        lote.save(update_fields=['status'])
        
        serializer = self.get_serializer(lote)
        return Response({
            "message": "Lote cancelado exitosamente",
            "lote": serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='validar-stock')
    def validar_stock(self, request, pk=None):
        from innoquim.apps.inventario.models import Kardex
        
        lote = self.get_object()
        materiales = MaterialProduccion.objects.filter(batch=lote).select_related(
            'raw_material'
        )
        
        validacion = []
        todo_ok = True
        
        for material in materiales:
            saldo = Kardex.obtener_saldo_actual(
                almacen=lote.almacen,
                item=material.raw_material
            )
            
            suficiente = saldo['cantidad'] >= material.used_quantity
            if not suficiente:
                todo_ok = False
            
            validacion.append({
                "materia_prima_id": material.raw_material.materia_prima_id,
                "nombre": material.raw_material.nombre,
                "codigo": material.raw_material.codigo,
                "requerido": float(material.used_quantity),
                "disponible": float(saldo['cantidad']),
                "unidad": material.unit.simbolo,
                "suficiente": suficiente
            })
        
        return Response({
            "valido": todo_ok,
            "almacen": lote.almacen.nombre,
            "materiales": validacion
        })