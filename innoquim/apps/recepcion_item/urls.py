from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RecepcionItemViewSet

# =================================================================
# RUTAS API RECEPCION ITEM
# =================================================================

# Router que genera automáticamente las rutas CRUD para el ViewSet
# DefaultRouter crea además un endpoint raíz con un navegador web
router = DefaultRouter()
router.register(r'recepcion-items', RecepcionItemViewSet)

# Incluye todas las rutas generadas por el router
urlpatterns = [
    path('', include(router.urls)),
]