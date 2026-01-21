from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import RecepcionMaterial
from .serializers import RecepcionMaterialSerializer

class RecepcionMaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar recepciones de material.
    
    Permite:
    - Listar todas las recepciones
    - Crear nuevas recepciones
    - Filtrar por almacén, materia prima, proveedor, fecha
    - Buscar por nombre de materia prima, proveedor, factura
    - Ordenar por fecha, total, proveedor
    """
    queryset = RecepcionMaterial.objects.all().select_related(
        'almacen', 'materia_prima', 'materia_prima__unidad_id'
    )
    serializer_class = RecepcionMaterialSerializer
    permission_classes = [IsAuthenticated]
    
    # Filtros y búsqueda
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'almacen': ['exact'],
        'materia_prima': ['exact'],
        'proveedor': ['exact', 'icontains'],
        'fecha_de_recepcion': ['exact', 'gte', 'lte'],
        'numero_de_factura': ['exact', 'icontains'],
    }
    search_fields = [
        'materia_prima__nombre',
        'proveedor', 
        'numero_de_factura',
        'observaciones'
    ]
    ordering_fields = [
        'fecha_de_recepcion',
        'fecha_creacion',
        'total',
        'proveedor',
        'materia_prima__nombre'
    ]
    ordering = ['-fecha_de_recepcion']
    
    def get_queryset(self):
        """
        Optimiza consultas y permite filtrados adicionales.
        """
        queryset = super().get_queryset()
        
        # Filtrar por rango de fechas si se proporcionan
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_de_recepcion__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_de_recepcion__lte=fecha_fin)
            
        # Filtrar por rango de totales si se proporcionan
        total_min = self.request.query_params.get('total_min', None)
        total_max = self.request.query_params.get('total_max', None)
        
        if total_min:
            queryset = queryset.filter(total__gte=total_min)
        if total_max:
            queryset = queryset.filter(total__lte=total_max)
            
        return queryset
