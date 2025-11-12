from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Almacen
from .serializers import AlmacenSerializer

class AlmacenViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar almacenes (secciones de almacenamiento).
    
    Proporciona las siguientes operaciones:
    - GET /almacenes/ : Lista todas las secciones del almacén
    - POST /almacenes/ : Crea una nueva sección
    - GET /almacenes/{id}/ : Obtiene los detalles de una sección específica
    - PUT /almacenes/{id}/ : Actualiza completamente una sección
    - PATCH /almacenes/{id}/ : Actualiza parcialmente una sección
    - DELETE /almacenes/{id}/ : Elimina una sección
    """
    # QuerySet que obtiene todos los almacenes de la base de datos
    queryset = Almacen.objects.all()
    
    # Serializador que convierte los datos a/desde JSON
    serializer_class = AlmacenSerializer
    
    # Permiso requerido: solo usuarios autenticados pueden acceder
    permission_classes = [IsAuthenticated]
