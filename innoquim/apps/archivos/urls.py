from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArchivoViewSet

# Crear router
router = DefaultRouter()
router.register(r'archivos', ArchivoViewSet, basename='archivo')

# URLs
urlpatterns = [
    path('', include(router.urls)),
]