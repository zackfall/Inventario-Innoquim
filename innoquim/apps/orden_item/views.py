from rest_framework import viewsets
from .models import OrdenItem
from .serializers import OrdenItemSerializer


class OrdenItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de OrdenItem.
    
    Endpoints generados automaticamente:
    - GET    /api/ordenes-items/          -> Listar todos los items
    - POST   /api/ordenes-items/          -> Crear nuevo item
    - GET    /api/ordenes-items/{id}/     -> Ver un item especifico
    - PUT    /api/ordenes-items/{id}/     -> Actualizar item completo
    - PATCH  /api/ordenes-items/{id}/     -> Actualizar item parcial
    - DELETE /api/ordenes-items/{id}/     -> Eliminar item
    
    Filtros disponibles:
    - ?order={id}    -> Filtrar por orden
    - ?product={id}  -> Filtrar por producto
    
    NOTA: Al crear/modificar/eliminar items, los totales de la orden
    se actualizan automaticamente via señales de Django
    """
    queryset = OrdenItem.objects.all()
    serializer_class = OrdenItemSerializer
    filterset_fields = ["order", "product"]