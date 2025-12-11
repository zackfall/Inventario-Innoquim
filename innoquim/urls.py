from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from innoquim.apps.unidad.views import UnidadViewSet
from innoquim.apps.producto.views import ProductoViewSet
from innoquim.apps.orden_cliente.views import OrdenClienteViewSet
from innoquim.apps.orden_item.views import OrdenItemViewSet
from innoquim.apps.lote_produccion.views import LoteProduccionViewSet
from innoquim.apps.material_produccion.views import MaterialProduccionViewSet

router = DefaultRouter()

router.register(r"unidades", UnidadViewSet, basename="unidad")
router.register(r"ordenes-cliente", OrdenClienteViewSet, basename="ordencliente")
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"orden-items", OrdenItemViewSet, basename="ordenitem")
router.register(r"lotes-produccion", LoteProduccionViewSet, basename="loteproduccion")
router.register(
    r"materiales-produccion", MaterialProduccionViewSet, basename="materialproduccion"
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("innoquim.apps.cliente.urls")), # API de Clientes
    path("api/", include("innoquim.apps.proveedor.urls")), # API de Proveedor
    path("api/", include("innoquim.apps.materia_prima.urls")), # API de Materia Prima
    path("api/", include("innoquim.apps.inventario_material.urls")), # API de Inventario_Material
    path("api/", include("innoquim.apps.pedido_material.urls")), # API de Pedido_material
    path('api/', include('innoquim.apps.orden_cliente.urls')), # API de Orden_Cliente
    path('api/', include('innoquim.apps.orden_item.urls')), # API de Orden_Item
    path("api/", include("innoquim.apps.usuario.urls")),
    path("api/", include(router.urls)),
]
