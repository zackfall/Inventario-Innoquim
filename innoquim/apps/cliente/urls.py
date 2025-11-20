from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

# Router automático de DRF que crea las rutas CRUD
# - Registrar el ViewSet crea endpoints REST estándar.
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')

urlpatterns = [
    path('', include(router.urls)),  # incluir rutas del router en la app
]