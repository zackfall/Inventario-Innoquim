from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArchivoViewSet

# Crear router para el ViewSet
router = DefaultRouter()
router.register(r'archivos', ArchivoViewSet, basename='archivo')

app_name = 'gestor_archivos'

urlpatterns = [
    path('', include(router.urls)),
]