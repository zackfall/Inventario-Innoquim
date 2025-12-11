from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdenClienteViewSet

# Router de DRF: genera automaticamente las rutas CRUD
router = DefaultRouter()
router.register(r'ordenes-clientes', OrdenClienteViewSet, basename='ordencliente')

urlpatterns = [
    path('', include(router.urls)),
]