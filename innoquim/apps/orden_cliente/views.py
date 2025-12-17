from rest_framework import viewsets
from .models import OrdenCliente
from .serializers import OrdenClienteSerializer


class OrdenClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de OrdenCliente.
    
    Endpoints generados automaticamente:
    - GET    /api/ordenes-clientes/          -> Listar todas las ordenes
    - POST   /api/ordenes-clientes/          -> Crear nueva orden
    - GET    /api/ordenes-clientes/{id}/     -> Ver una orden especifica
    - PUT    /api/ordenes-clientes/{id}/     -> Actualizar orden completa
    - PATCH  /api/ordenes-clientes/{id}/     -> Actualizar orden parcial
    - DELETE /api/ordenes-clientes/{id}/     -> Eliminar orden
    
    Filtros disponibles:
    - ?client={id}   -> Filtrar por cliente
    - ?status={status} -> Filtrar por estado
    - ?search={codigo} -> Buscar por codigo de orden
    """
    queryset = OrdenCliente.objects.all()
    serializer_class = OrdenClienteSerializer
    filterset_fields = ["client", "status"]
    search_fields = ["order_code"]