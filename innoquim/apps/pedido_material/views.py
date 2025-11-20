from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PedidoMaterial
from .serializers import PedidoMaterialSerializer


class PedidoMaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de PedidoMaterial.
    
    El usuario_registro se asigna automaticamente del usuario logueado.
    """
    queryset = PedidoMaterial.objects.all()
    serializer_class = PedidoMaterialSerializer
    permission_classes = [IsAuthenticated]  # Requiere estar logueado
    
    def perform_create(self, serializer):
        """
        Asigna automaticamente el usuario_registro al usuario logueado.
        """
        serializer.save(usuario_registro=self.request.user)
    
    def get_queryset(self):
        """
        Permite filtrar pedidos via query params.
        Ejemplos:
        - /api/pedidos-materiales/?proveedor_id=PROV01
        - /api/pedidos-materiales/?fecha_pedido=2025-11-15
        """
        queryset = PedidoMaterial.objects.all()
        
        proveedor_id = self.request.query_params.get('proveedor_id', None)
        fecha_pedido = self.request.query_params.get('fecha_pedido', None)
        
        if proveedor_id:
            queryset = queryset.filter(proveedor_id=proveedor_id)
        if fecha_pedido:
            queryset = queryset.filter(fecha_pedido=fecha_pedido)
        
        return queryset