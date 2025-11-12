from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Entrega
from .serializers import EntregaSerializer

class EntregaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar entregas.
    """
    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado is not None:
            queryset = queryset.filter(estado=estado.lower())
        
        # Filtrar por fecha
        fecha = self.request.query_params.get('fecha', None)
        if fecha is not None:
            queryset = queryset.filter(fecha_entrega__date=fecha)
            
        return queryset

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint para cambiar el estado de una entrega
        """
        entrega = self.get_object()
        nuevo_estado = request.data.get('estado', '').lower()
        estados_permitidos = ['pendiente', 'en_proceso', 'entregado', 'cancelado']
        
        if nuevo_estado not in estados_permitidos:
            return Response(
                {"error": f"Estado no válido. Estados permitidos: {', '.join(estados_permitidos)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        entrega.estado = nuevo_estado
        entrega.save()
        return Response(EntregaSerializer(entrega).data)
