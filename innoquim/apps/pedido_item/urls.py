from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PedidoItemViewSet

router = DefaultRouter()
router.register(r'pedido-items', PedidoItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]