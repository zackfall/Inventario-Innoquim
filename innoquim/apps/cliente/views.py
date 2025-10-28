from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # Para desarrollo, permite acceso sin autenticación
from .models import Cliente
from .serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Cliente.
    - Usar permisos más restrictivos en producción.
    - queryset/serializer_class mantienen la fuente de datos y formato.
    - Si se requieren filtros/paginación personalizados, agregarlos aquí.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]  # Solo para desarrollo, luego cambiar por autenticación