from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AlmacenViewSet

router = DefaultRouter()
router.register(r'almacenes', AlmacenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]