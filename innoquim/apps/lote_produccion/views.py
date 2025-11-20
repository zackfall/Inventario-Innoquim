from rest_framework import viewsets
from .models import LoteProduccion
from .serializers import LoteProduccionSerializer


class LoteProduccionViewSet(viewsets.ModelViewSet):
    queryset = LoteProduccion.objects.all()
    serializer_class = LoteProduccionSerializer
    filterset_fields = ["product", "status", "production_manager"]
    search_fields = ["batch_code"]
