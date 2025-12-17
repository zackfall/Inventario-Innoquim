from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdenItemViewSet

# Router de DRF: genera automaticamente las rutas CRUD
router = DefaultRouter()
router.register(r'ordenes-items', OrdenItemViewSet, basename='ordenitem')

urlpatterns = [
    path('', include(router.urls)),
]