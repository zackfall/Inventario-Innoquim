from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RecepcionMaterial
from .serializers import RecepcionMaterialSerializer

class RecepcionMaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar recepciones de material.
    """
    queryset = RecepcionMaterial.objects.all().select_related('id_almacen')
    serializer_class = RecepcionMaterialSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por almacén si se proporciona en la URL
        almacen_id = self.request.query_params.get('almacen', None)
        if almacen_id is not None:
            queryset = queryset.filter(id_almacen=almacen_id)
        return queryset
