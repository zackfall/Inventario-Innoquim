from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MateriaPrimaViewSet

# Router de DRF: genera automaticamente las rutas CRUD
router = DefaultRouter()
router.register(r'materias-primas', MateriaPrimaViewSet, basename='materia-prima')

urlpatterns = [
    path('', include(router.urls)),
]