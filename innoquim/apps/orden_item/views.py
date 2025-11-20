from rest_framework import viewsets
from .models import OrdenItem
from .serializers import OrdenItemSerializer


class OrdenItemViewSet(viewsets.ModelViewSet):
    queryset = OrdenItem.objects.all()
    serializer_class = OrdenItemSerializer
    filterset_fields = ["order", "product"]
