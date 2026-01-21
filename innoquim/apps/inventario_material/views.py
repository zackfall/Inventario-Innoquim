from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import InventarioMaterial
from .serializers import InventarioMaterialSerializer


class InventarioMaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de InventarioMaterial (genérico).

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
        - /api/inventario-materiales/?tipo=producto
        - /api/inventario-materiales/?object_id=MP000001
        """
        queryset = InventarioMaterial.objects.all()

        almacen_id = self.request.query_params.get('almacen_id')
        tipo = self.request.query_params.get('tipo')  # 'materia_prima' | 'producto'
        object_id = self.request.query_params.get('object_id')

        if almacen_id:
            queryset = queryset.filter(almacen_id=almacen_id)
        if tipo:
            tipo = tipo.lower()
            if tipo in ['materia_prima', 'mp', 'raw']:
                queryset = queryset.filter(content_type__model='materia_prima')
            elif tipo in ['producto', 'product']:
                queryset = queryset.filter(content_type__model='producto')
        if object_id:
            queryset = queryset.filter(object_id=object_id)

        return queryset