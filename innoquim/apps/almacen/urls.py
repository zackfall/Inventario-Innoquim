from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AlmacenViewSet

# Router que genera automáticamente las rutas CRUD para el ViewSet
router = DefaultRouter()
router.register(r'almacenes', AlmacenViewSet)

# Incluye todas las rutas generadas por el router
urlpatterns = [
    path('', include(router.urls)),
]