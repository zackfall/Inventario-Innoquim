from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PedidoItem
from .serializers import PedidoItemSerializer

class PedidoItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar items de pedido.
    """
    queryset = PedidoItem.objects.all().select_related('id_unidad_medida')
    serializer_class = PedidoItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por unidad de medida
        unidad_id = self.request.query_params.get('unidad', None)
        if unidad_id is not None:
            queryset = queryset.filter(id_unidad_medida=unidad_id)
        return queryset

    @action(detail=True, methods=['post'])
    def actualizar_cantidad_recibida(self, request, pk=None):
        """
        Endpoint para actualizar la cantidad recibida de un item
        """
        item = self.get_object()
        nueva_cantidad = request.data.get('cantidad_recibida', 0)
        
        if nueva_cantidad > item.cantidad_solicitada:
            return Response(
                {"error": "La cantidad recibida no puede ser mayor que la solicitada"},
                status=400
            )
            
        item.cantidad_recibida = nueva_cantidad
        item.save()
        return Response(PedidoItemSerializer(item).data)
