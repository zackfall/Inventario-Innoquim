from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventarioMaterialViewSet

# Router de DRF: genera automaticamente las rutas CRUD
router = DefaultRouter()
router.register(r'inventario-materiales', InventarioMaterialViewSet, basename='inventario-material')

urlpatterns = [
    path('', include(router.urls)),
]