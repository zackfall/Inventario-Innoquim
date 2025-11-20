from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import MateriaPrima
from .serializers import MateriaPrimaSerializer


class MateriaPrimaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de MateriaPrima.
    
    Endpoints generados automaticamente:
    - GET    /api/materias-primas/          -> Listar todas
    - POST   /api/materias-primas/          -> Crear nueva
    - GET    /api/materias-primas/{id}/     -> Ver una especifica
    - PUT    /api/materias-primas/{id}/     -> Actualizar completa
    - PATCH  /api/materias-primas/{id}/     -> Actualizar parcial
    - DELETE /api/materias-primas/{id}/     -> Eliminar
    
    IMPORTANTE: permission_classes = [AllowAny] es SOLO para desarrollo
    """
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer
    permission_classes = [AllowAny]  # TODO: Cambiar en produccion