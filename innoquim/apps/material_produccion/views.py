from rest_framework import viewsets
from .models import MaterialProduccion
from .serializers import MaterialProduccionSerializer


class MaterialProduccionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar materiales utilizados en la producción."""
    queryset = MaterialProduccion.objects.all().order_by("-created_at")
    serializer_class = MaterialProduccionSerializer
    filterset_fields = ["batch", "raw_material"]
    search_fields = ["raw_material__name", "batch__batch_code"]
