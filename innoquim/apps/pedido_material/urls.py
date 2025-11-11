from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoMaterialViewSet

router = DefaultRouter()
router.register(r'pedidos-materiales', PedidoMaterialViewSet, basename='pedido-material')

urlpatterns = [
    path('', include(router.urls)),
]