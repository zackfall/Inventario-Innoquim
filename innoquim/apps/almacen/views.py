from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Almacen
from .serializers import AlmacenSerializer

class AlmacenViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar almacenes.
    """
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]
