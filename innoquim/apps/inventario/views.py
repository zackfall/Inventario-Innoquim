from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from .models import Kardex
from .serializers import KardexSerializer


class KardexViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de Kardex.

    IMPORTANTE: Los registros de Kardex NO se crean directamente por API.
    Se crean automáticamente cuando:
    - Se recibe material (RecepcionItem)
    - Se consume material en producción (MaterialProduccion)
    - Se vende producto (OrdenItem)
    - Se hacen ajustes manuales de inventario

    Endpoints disponibles:
    - GET /api/kardex/ - Listar todos los movimientos
    - GET /api/kardex/{id}/ - Ver un movimiento específico
    - GET /api/kardex/saldo/ - Consultar saldo actual de un item
    - GET /api/kardex/historial/ - Ver historial de un item
    """

    queryset = Kardex.objects.all().select_related("almacen", "usuario")
    serializer_class = KardexSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Permite filtrar Kardex por:
        - almacen: ID del almacén
        - tipo_movimiento: ENTRADA o SALIDA
        - motivo: COMPRA, PRODUCCION, VENTA, etc.
        - fecha_desde: filtro de fecha inicio
        - fecha_hasta: filtro de fecha fin
        """
        queryset = super().get_queryset()

        # Filtros básicos
        almacen = self.request.query_params.get("almacen", None)
        if almacen:
            queryset = queryset.filter(almacen_id=almacen)

        tipo_movimiento = self.request.query_params.get("tipo_movimiento", None)
        if tipo_movimiento:
            queryset = queryset.filter(tipo_movimiento=tipo_movimiento)

        motivo = self.request.query_params.get("motivo", None)
        if motivo:
            queryset = queryset.filter(motivo=motivo)

        # Filtros de fecha
        fecha_desde = self.request.query_params.get("fecha_desde", None)
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)

        fecha_hasta = self.request.query_params.get("fecha_hasta", None)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        return queryset

    @action(detail=False, methods=["get"])
    def saldo(self, request):
        """
        Endpoint para consultar el saldo actual de un item en un almacén.

        Parámetros requeridos:
        - almacen_id: ID del almacén
        - materia_prima_id: ID de materia prima (si aplica)
          O
        - producto_id: ID de producto (si aplica)

        Ejemplo:
        GET /api/kardex/saldo/?almacen_id=1&materia_prima_id=MP000001
        """
        almacen_id = request.query_params.get("almacen_id")
        materia_prima_id = request.query_params.get("materia_prima_id")
        producto_id = request.query_params.get("producto_id")

        if not almacen_id:
            return Response(
                {"error": "almacen_id es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not materia_prima_id and not producto_id:
            return Response(
                {"error": "Debe proporcionar materia_prima_id o producto_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from innoquim.apps.almacen.models import Almacen

            almacen = Almacen.objects.get(id=almacen_id)

            # Obtener el item (MateriaPrima o Producto)
            if materia_prima_id:
                from innoquim.apps.materia_prima.models import MateriaPrima

                item = MateriaPrima.objects.get(materia_prima_id=materia_prima_id)
            else:
                from innoquim.apps.producto.models import Producto

                item = Producto.objects.get(id=producto_id)

            # Obtener saldo actual
            saldo = Kardex.obtener_saldo_actual(almacen, item)

            return Response(
                {
                    "almacen_id": almacen_id,
                    "item_id": materia_prima_id or producto_id,
                    "item_tipo": "materia_prima" if materia_prima_id else "producto",
                    **saldo,
                }
            )

        except (Almacen.DoesNotExist, Exception) as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def historial(self, request):
        """
        Endpoint para consultar el historial completo de un item en un almacén.

        Parámetros requeridos:
        - almacen_id: ID del almacén
        - materia_prima_id: ID de materia prima (si aplica)
          O
        - producto_id: ID de producto (si aplica)

        Parámetros opcionales:
        - fecha_desde: Filtrar desde fecha
        - fecha_hasta: Filtrar hasta fecha

        Ejemplo:
        GET /api/kardex/historial/?almacen_id=1&materia_prima_id=MP000001
        """
        almacen_id = request.query_params.get("almacen_id")
        materia_prima_id = request.query_params.get("materia_prima_id")
        producto_id = request.query_params.get("producto_id")

        if not almacen_id:
            return Response(
                {"error": "almacen_id es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not materia_prima_id and not producto_id:
            return Response(
                {"error": "Debe proporcionar materia_prima_id o producto_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Determinar el content_type
            if materia_prima_id:
                from innoquim.apps.materia_prima.models import MateriaPrima

                content_type = ContentType.objects.get_for_model(MateriaPrima)
                object_id = materia_prima_id
            else:
                from innoquim.apps.producto.models import Producto

                content_type = ContentType.objects.get_for_model(Producto)
                object_id = producto_id

            # Filtrar registros
            queryset = Kardex.objects.filter(
                almacen_id=almacen_id, content_type=content_type, object_id=object_id
            ).order_by("fecha", "id")

            # Aplicar filtros de fecha si existen
            fecha_desde = request.query_params.get("fecha_desde")
            if fecha_desde:
                queryset = queryset.filter(fecha__gte=fecha_desde)

            fecha_hasta = request.query_params.get("fecha_hasta")
            if fecha_hasta:
                queryset = queryset.filter(fecha__lte=fecha_hasta)

            serializer = KardexSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
