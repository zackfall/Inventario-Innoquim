from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LoteProduccion
from .serializers import LoteProduccionSerializer
from innoquim.apps.material_produccion.models import MaterialProduccion
from innoquim.apps.material_produccion.serializers import MaterialProduccionSerializer


class LoteProduccionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar lotes de producción."""
    queryset = LoteProduccion.objects.all().order_by("-production_date")
    serializer_class = LoteProduccionSerializer
    filterset_fields = ["product", "status", "production_manager"]
    search_fields = ["batch_code", "product__name"]

    @action(detail=True, methods=["get"], url_path="materiales")
    def list_materiales(self, request, pk=None):
        """Obtener todos los materiales de un lote."""
        lote = self.get_object()
        materiales = MaterialProduccion.objects.filter(batch=lote)
        serializer = MaterialProduccionSerializer(materiales, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="materiales")
    def add_material(self, request, pk=None):
        """Agregar un material a un lote."""
        lote = self.get_object()
        serializer = MaterialProduccionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(batch=lote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, 
        methods=["get", "put", "delete"], 
        url_path=r"materiales/(?P<material_id>\d+)"
    )
    def manage_material(self, request, pk=None, material_id=None):
        """Gestionar un material específico del lote."""
        lote = self.get_object()
        material = get_object_or_404(MaterialProduccion, id=material_id, batch=lote)
        
        if request.method == "GET":
            serializer = MaterialProduccionSerializer(material)
            return Response(serializer.data)
        
        elif request.method == "PUT":
            serializer = MaterialProduccionSerializer(material, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == "DELETE":
            material.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
