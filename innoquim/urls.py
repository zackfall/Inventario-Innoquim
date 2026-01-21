from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

from innoquim.apps.unidad.views import UnidadViewSet
from innoquim.apps.producto.views import ProductoViewSet
from innoquim.apps.lote_produccion.views import LoteProduccionViewSet
from innoquim.apps.material_produccion.views import MaterialProduccionViewSet
from innoquim.apps.usuario.health_views import health_check

router = DefaultRouter()

router.register(r"unidades", UnidadViewSet, basename="unidad")
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"lotes-produccion", LoteProduccionViewSet, basename="loteproduccion")
router.register(
    r"materiales-produccion", MaterialProduccionViewSet, basename="materialproduccion"
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/', include('innoquim.apps.archivos.urls')),  # API del Gestor de Archivos
    path("api/health/", health_check, name="health-check"),  # Health check endpoint
    path("api/", include("innoquim.apps.categoria.urls")),  # API de Categorias
    path("api/", include("innoquim.apps.cliente.urls")),  # API de Clientes
    path("api/", include("innoquim.apps.proveedor.urls")),  # API de Proveedor
    path("api/", include("innoquim.apps.materia_prima.urls")),  # API de Materia Prima
    path("api/", include("innoquim.apps.inventario_material.urls")),  # API de Inventario_Material
    path("api/", include("innoquim.apps.inventario.urls")),  # API de Kardex
    path("api/", include("innoquim.apps.pedido_material.urls")),  # API de Pedido_material
    path("api/", include("innoquim.apps.orden_cliente.urls")),  # API de Orden_Cliente
    path("api/", include("innoquim.apps.orden_item.urls")),  # API de Orden_Item
    path("api/", include("innoquim.apps.lote_produccion.urls")),  # API de Lote_Produccion
    path("api/", include("innoquim.apps.usuario.urls")),
    path("api/", include("innoquim.apps.almacen.urls")),
    path("api/", include("innoquim.apps.recepcion_material.urls")),
    path("api/", include("innoquim.apps.recepcion_item.urls")),
    path("api/", include(router.urls)),
]
