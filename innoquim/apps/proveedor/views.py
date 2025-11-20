from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Proveedor
from .serializers import ProveedorSerializer


class ProveedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD completas de Proveedor.
    
    Endpoints disponibles:
    - GET /api/proveedores/ - Listar todos los proveedores
    - POST /api/proveedores/ - Crear nuevo proveedor
    - GET /api/proveedores/{id}/ - Obtener un proveedor específico
    - PUT /api/proveedores/{id}/ - Actualizar proveedor completo
    - PATCH /api/proveedores/{id}/ - Actualizar proveedor parcial
    - DELETE /api/proveedores/{id}/ - Eliminar proveedor
    """
    
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [AllowAny]  # TODO: Cambiar por autenticación en producción
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método create para personalizar la respuesta
        al crear un nuevo proveedor.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Proveedor creado exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )