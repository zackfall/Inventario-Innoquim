from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import RecepcionItem
from .serializers import RecepcionItemSerializer

# =================================================================
# VISTAS API RECEPCION ITEM
# =================================================================
class RecepcionItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar items de recepción.
    
    Un RecepcionItem representa un producto específico dentro de una recepción.
    Por ejemplo, en una recepción pueden haber múltiples items de diferentes
    materias primas.
    
    Operaciones disponibles:
    - GET /recepcion-items/ : Lista todos los items de recepción
    - POST /recepcion-items/ : Crea un nuevo item
    - GET /recepcion-items/{id}/ : Obtiene detalles de un item
    - PUT /recepcion-items/{id}/ : Actualiza completamente un item
    - PATCH /recepcion-items/{id}/ : Actualiza parcialmente un item
    - DELETE /recepcion-items/{id}/ : Elimina un item
    
    Filtros disponibles:
    - ?recepcion=id : Filtra items de una recepción específica
    - ?lote=numero : Filtra items por número de lote
    """
    
    # QuerySet optimizado con select_related para evitar N+1 queries
    # Precarga las relaciones para mejor rendimiento
    queryset = RecepcionItem.objects.all().select_related(
        'id_recepcion_material',
        'id_materia_prima',
        'id_unidad'
    )
    
    # Serializador que convierte los datos a/desde JSON
    serializer_class = RecepcionItemSerializer
    
    # Solo usuarios autenticados pueden acceder a estos endpoints
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Personaliza el QuerySet según parámetros de filtrado.
        Permite filtrar por recepción material y lote.
        """
        queryset = super().get_queryset()
        
        # Filtrar por ID de recepción material si se proporciona
        # Ej: GET /recepcion-items/?recepcion=1
        recepcion_id = self.request.query_params.get('recepcion', None)
        if recepcion_id is not None:
            queryset = queryset.filter(id_recepcion_material=recepcion_id)
        
        # Filtrar por número de lote si se proporciona
        # Ej: GET /recepcion-items/?lote=LOT-2025-001
        lote = self.request.query_params.get('lote', None)
        if lote is not None:
            queryset = queryset.filter(lote=lote)
            
        return queryset
