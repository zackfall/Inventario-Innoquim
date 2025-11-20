from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import InventarioMaterial
from .serializers import InventarioMaterialSerializer


class InventarioMaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de InventarioMaterial.
    
    Endpoints generados automaticamente:
    - GET    /api/inventario-materiales/          -> Listar todos
    - POST   /api/inventario-materiales/          -> Crear nuevo
    - GET    /api/inventario-materiales/{id}/     -> Ver uno especifico
    - PUT    /api/inventario-materiales/{id}/     -> Actualizar completo
    - PATCH  /api/inventario-materiales/{id}/     -> Actualizar parcial
    - DELETE /api/inventario-materiales/{id}/     -> Eliminar
    
    IMPORTANTE: permission_classes = [AllowAny] es SOLO para desarrollo
    """
    queryset = InventarioMaterial.objects.all()
    serializer_class = InventarioMaterialSerializer
    permission_classes = [AllowAny]  # TODO: Cambiar en produccion
    
    def get_queryset(self):
        """
        Permite filtrar inventarios via query params.
        Ejemplos:
        - /api/inventario-materiales/?almacen_id=1
        - /api/inventario-materiales/?materia_prima_id=MP000001
        """
        queryset = InventarioMaterial.objects.all()
        
        almacen_id = self.request.query_params.get('almacen_id', None)
        materia_prima_id = self.request.query_params.get('materia_prima_id', None)
        
        if almacen_id:
            queryset = queryset.filter(almacen_id=almacen_id)
        if materia_prima_id:
            queryset = queryset.filter(materia_prima_id=materia_prima_id)
        
        return queryset