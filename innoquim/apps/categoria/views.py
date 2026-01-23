from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías.
    
    Soporta filtrado por tipo mediante query params:
    - GET /api/categorias/?tipo=PRODUCT
    - GET /api/categorias/?tipo=RAW_MATERIAL
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Permite filtrar categorías por tipo.
        Ejemplo: /api/categorias/?tipo=PRODUCT
        """
        queryset = super().get_queryset()
        
        # Filtrar por tipo si se proporciona en los query params
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset