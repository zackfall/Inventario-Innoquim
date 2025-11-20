from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RecepcionItemViewSet

router = DefaultRouter()
router.register(r'recepcion-items', RecepcionItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]