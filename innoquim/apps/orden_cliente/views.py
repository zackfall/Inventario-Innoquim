from rest_framework import viewsets
from .models import OrdenCliente
from .serializers import OrdenClienteSerializer


class OrdenClienteViewSet(viewsets.ModelViewSet):
    queryset = OrdenCliente.objects.all()
    serializer_class = OrdenClienteSerializer
    filterset_fields = ["client", "status"]
    search_fields = ["order_code"]
