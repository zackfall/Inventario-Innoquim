from rest_framework import viewsets
from .models import MaterialProduccion
from .serializers import MaterialProduccionSerializer


class MaterialProduccionViewSet(viewsets.ModelViewSet):
    queryset = MaterialProduccion.objects.all()
    serializer_class = MaterialProduccionSerializer
    filterset_fields = ["batch", "raw_material"]
