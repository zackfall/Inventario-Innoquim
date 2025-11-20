from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RecepcionItem
from .serializers import RecepcionItemSerializer

class RecepcionItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar items de recepción.
    """
    queryset = RecepcionItem.objects.all().select_related(
        'id_recepcion_material',
        'id_unidad'
    )
    serializer_class = RecepcionItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por recepción material si se proporciona
        recepcion_id = self.request.query_params.get('recepcion', None)
        if recepcion_id is not None:
            queryset = queryset.filter(id_recepcion_material=recepcion_id)
        # Filtrar por lote si se proporciona
        lote = self.request.query_params.get('lote', None)
        if lote is not None:
            queryset = queryset.filter(lote=lote)
        return queryset
